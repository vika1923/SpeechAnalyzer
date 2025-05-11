from gramformer import Gramformer

# set_seed(1212)

gf = Gramformer(models = 1, use_gpu=False) # 1=corrector, 2=detector


influent_sentences = [
    "house near hospital is big enough to accomodate whole family.", "i loves sport.", "helicopter fly low.", "helicopter flies law, but spaceships fly high."
]

def get_corrected_text(influent_sentences):
    edited_sentences = []
    for influent_sentence in influent_sentences:
        corrected_sentences = gf.correct(influent_sentence, max_candidates=1)
        for corrected_sentence in corrected_sentences:
            edited_sentences.append(gf.highlight(influent_sentence, corrected_sentence))
    return edited_sentences

def get_parsed_corrected_text(corrected_sentences):
    mistake_indices = []
    for corrected_sentence in corrected_sentences:
        # Find all <c> tags in the text
        start_idx = 0
        while True:
            # Find the start of a correction tag
            tag_start = corrected_sentence.find('<c', start_idx)
            if tag_start == -1:
                break

            # Find the end of the opening tag
            tag_end = corrected_sentence.find('>', tag_start)
                
            # Find the end of the correction tag
            closing_tag = corrected_sentence.find('</c>', tag_end)
                
            # Get the incorrect word between the tags
            incorrect_word = corrected_sentence[tag_end + 1:closing_tag]
            
            # Calculate the start and end indices
            start_index = tag_start
            end_index = tag_start + len(incorrect_word)-1
            
            mistake_indices.append((start_index, end_index))
            
            # Move the search start position after this correction
            start_idx = closing_tag + 4
            
    return mistake_indices