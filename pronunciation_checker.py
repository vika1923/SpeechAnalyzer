import os
from faster_whisper import WhisperModel
from typing import Dict, List, Tuple
from custom_types import TimeStamp
import numpy as np
import eng_to_ipa
from dtwalign import dtw_from_distance_matrix
import re

class PronunciationAnalyzer:
    def __init__(self, model_size: str = "large-v3"):
        """
        Initialize the pronunciation analyzer with Whisper model.
        
        Args:
            model_size (str): Size of the Whisper model to use (tiny, base, small, medium, large-v3)
        """
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
    def _convert_to_phonemes(self, text: str) -> str:
        """Convert text to IPA phonemes."""
        phonemes = eng_to_ipa.convert(text)
        return phonemes.replace('*', '')
        
    def _get_word_distance_matrix(self, words_estimated: list, words_real: list) -> np.ndarray:
        """Calculate distance matrix between estimated and real words."""
        number_of_real_words = len(words_real)
        number_of_estimated_words = len(words_estimated)
        
        word_distance_matrix = np.zeros((number_of_estimated_words, number_of_real_words))
        for idx_estimated in range(number_of_estimated_words):
            for idx_real in range(number_of_real_words):
                # Convert both words to phonemes for comparison
                est_phonemes = self._convert_to_phonemes(words_estimated[idx_estimated])
                real_phonemes = self._convert_to_phonemes(words_real[idx_real])
                # Calculate edit distance between phonemes
                word_distance_matrix[idx_estimated, idx_real] = self._edit_distance(est_phonemes, real_phonemes)
                
        return word_distance_matrix
        
    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
            
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
            
        return previous_row[-1]
        
    def _get_letter_accuracy(self, real_word: str, transcribed_word: str) -> List[int]:
        """Analyze which letters were transcribed correctly."""
        is_letter_correct = [None] * len(real_word)
        for idx, letter in enumerate(real_word):
            if idx >= len(transcribed_word):
                is_letter_correct[idx] = 0
                continue
            letter = letter.lower()
            transcribed_letter = transcribed_word[idx].lower()
            if letter == transcribed_letter or letter in '.,!?':
                is_letter_correct[idx] = 1
            else:
                is_letter_correct[idx] = 0
        return is_letter_correct
        
    def analyze_pronunciation(self, audio_file_path: str, target_text: str) -> Dict:
        """
        Analyze pronunciation of an audio file against target text.
        
        Args:
            audio_file_path (str): Path to the audio file to analyze
            target_text (str): The text that should be pronounced
            
        Returns:
            Dict containing analysis results with word-level feedback
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
        # Transcribe the audio with word timestamps
        segments, _ = self.model.transcribe(
            audio_file_path,
            language="en",
            beam_size=5,
            word_timestamps=True
        )
        
        # Process the transcription
        transcribed_words = []
        for segment in segments:
            for word in segment.words or []:
                text = word.word.strip()
                if text:
                    transcribed_words.append(text)
        
        # Get target words
        target_words = [word.strip() for word in target_text.split()]
        
        # Get word distance matrix
        word_distance_matrix = self._get_word_distance_matrix(transcribed_words, target_words)
        
        # Use DTW to align words
        alignment = dtw_from_distance_matrix(word_distance_matrix.T)
        mapped_indices = alignment.get_warping_path()[:len(transcribed_words)]
        
        # Analyze each word
        word_analysis = []
        for i, target_word in enumerate(target_words):
            # Find the best matching transcribed word
            matching_indices = np.where(mapped_indices == i)[0]
            if len(matching_indices) == 0:
                transcribed_word = "-"
                score = 0.0
            else:
                # Get the transcribed word with lowest distance
                distances = [word_distance_matrix[idx, i] for idx in matching_indices]
                best_idx = matching_indices[np.argmin(distances)]
                transcribed_word = transcribed_words[best_idx]
                # Calculate score based on phoneme distance
                max_distance = max(len(self._convert_to_phonemes(target_word)), 
                                 len(self._convert_to_phonemes(transcribed_word)))
                score = 1.0 - (word_distance_matrix[best_idx, i] / max_distance) if max_distance > 0 else 0.0
            
            # Get letter-level analysis
            letter_accuracy = self._get_letter_accuracy(target_word, transcribed_word)
            incorrect_letters = [target_word[i] for i, correct in enumerate(letter_accuracy) if correct == 0]
            
            word_analysis.append({
                'word': target_word,
                'transcribed': transcribed_word,
                'score': score,
                'mispronounced': score < 0.7,
                'feedback': f"Mispronounced letters: {', '.join(incorrect_letters)}" if incorrect_letters else "Correctly pronounced"
            })
        
        # Calculate overall score
        overall_score = np.mean([word['score'] for word in word_analysis]) if word_analysis else 0.0
        
        return {
            'overall_score': overall_score,
            'word_analysis': word_analysis
        }

def print_pronunciation_analysis(analysis: Dict) -> None:
    """
    Print the pronunciation analysis results in a readable format.
    
    Args:
        analysis (Dict): The analysis results from analyze_pronunciation
    """
    print(f"\nOverall Pronunciation Score: {analysis['overall_score']:.2f}")
    print("\nWord-by-Word Analysis:")
    print("-" * 50)
    
    for word in analysis['word_analysis']:
        status = "❌ MISPRONOUNCED" if word['mispronounced'] else "✅ CORRECT"
        print(f"\nWord: {word['word']}")
        print(f"Transcribed as: {word['transcribed']}")
        print(f"Status: {status}")
        print(f"Score: {word['score']:.2f}")
        if word['mispronounced']:
            print(f"Feedback: {word['feedback']}")
        print("-" * 50)

# Example usage
if __name__ == "__main__":
    analyzer = PronunciationAnalyzer()
    
    # Example usage
    audio_file = "path/to/your/audio.wav"
    target_text = "Hello world"
    
    try:
        analysis = analyzer.analyze_pronunciation(audio_file, target_text)
        print_pronunciation_analysis(analysis)
    except Exception as e:
        print(f"Error: {str(e)}")
