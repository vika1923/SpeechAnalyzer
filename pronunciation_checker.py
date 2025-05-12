import os
from faster_whisper import WhisperModel
from typing import Dict, List, Tuple
from custom_types import TimeStamp
import numpy as np

class PronunciationAnalyzer:
    def __init__(self, model_size: str = "large-v3"):
        """
        Initialize the pronunciation analyzer with Whisper model.
        
        Args:
            model_size (str): Size of the Whisper model to use (tiny, base, small, medium, large-v3)
        """
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
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
        transcribed_words = {}
        for segment in segments:
            for word in segment.words or []:
                start = round(word.start, 2)
                end = round(word.end, 2)
                text = word.word.strip()
                if text:
                    transcribed_words[(start, end)] = text
        
        # Compare with target text
        target_words = target_text.lower().split()
        transcribed_text = ' '.join(word.lower() for word in transcribed_words.values())
        transcribed_words_list = transcribed_text.split()
        
        # Analyze each word
        word_analysis = []
        min_len = min(len(target_words), len(transcribed_words_list))
        
        for i in range(min_len):
            target_word = target_words[i]
            transcribed_word = transcribed_words_list[i]
            
            # Calculate similarity score (simple exact match for now)
            score = 1.0 if target_word == transcribed_word else 0.0
            
            word_analysis.append({
                'word': target_word,
                'transcribed': transcribed_word,
                'score': score,
                'mispronounced': score < 0.7,
                'feedback': f"Expected '{target_word}' but heard '{transcribed_word}'" if score < 0.7 else "Correctly pronounced"
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
