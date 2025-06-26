from gramformer import Gramformer 

# set_seed(1212)

gf = Gramformer(models = 1, use_gpu=False) # 1=corrector, 2=detector


def get_corrected_text(influent_sentences):
    edited_sentences = []
    for influent_sentence in influent_sentences:
        corrected_sentences = gf.correct(influent_sentence, max_candidates=1)
        for corrected_sentence in corrected_sentences:
            edited_sentences.append(gf.highlight(influent_sentence, corrected_sentence))
    print("corrected with gramformer in grammar_checker")
    return edited_sentences

def get_parsed_corrections(corrected_sentences):
    mistake_indices = []
    for corrected_sentence in corrected_sentences:
        # Find all <c> tags in the text
        start_idx = 0
        while True:
            # print(corrected_sentence)
            # Find the start of a correction tag
            tag_start = corrected_sentence.find('<', start_idx)
            if tag_start == -1:
                # print("no opening tag")
                break

            # Find the end of the opening tag
            tag_end = corrected_sentence.find('>', tag_start)
                
            # Find the end of the correction tag
            closing_tag = corrected_sentence.find('</', tag_end)
                
            # Get the incorrect word between the tags
            incorrect_word = corrected_sentence[tag_end + 1:closing_tag]

            edit=corrected_sentence.find("edit='")
            edit_end=corrected_sentence[edit+6:].find("'")
            # print("EDIT:", corrected_sentence[edit+6:edit+7+edit_end])
            
            # Calculate the start and end indices
            start_index = tag_start
            end_index = tag_start + len(incorrect_word)-1
            
            mistake_indices.append(((start_index, end_index), corrected_sentence[edit+6:edit+6+edit_end]))
            
            # Move the search start position after this correction
            start_idx = closing_tag + 4
            
    return mistake_indices

# t = get_corrected_text(["hello! my name Karl.", 'how is you doing.', "this is a my dog."])
# print(t)
# print(get_parsed_corrections(t))
# print(get_parsed_corrections(t))
