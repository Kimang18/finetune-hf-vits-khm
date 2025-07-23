from typing import List, Dict
from khmernltk import word_tokenize
import tha.normalize
import tha.repeater
import tha.normalize
import tha.datetime
import tha.decimals
import tha.ordinals


def process_repeater(words: List[str]) -> List[str]:
    fake_tokens = []
    for word in words:
        if word == 'ៗ':
            break
        fake_tokens.append(word)
    if len(fake_tokens) < len(words): # there is repeater
        def fake_tokenizer(_):
            return fake_tokens
        transcription = tha.repeater.processor(' '.join(words), tokenizer=fake_tokenizer)
        words = [word for word in word_tokenize(transcription.replace('▁', ''), return_tokens=True) if word != ' ']
    return words


def transform_khmer_sentence(ds) -> Dict:
    transcription = tha.normalize.processor(ds["transcription"])
    words = [w for w in word_tokenize(transcription, return_tokens=True) if w != " "]
    # check repeater
    old_words = []
    while words != old_words:
        old_words = list(words)
        words = process_repeater(words)
    # standardize numbers and times
    for j in range(len(words)):
        w = words[j]
        if "$" in w or "៛" in w:
            w = tha.currency.processor(w)
        else:
            w = tha.datetime.time_processor(w)
            w = tha.datetime.date_processor(w)
            w = tha.decimals.processor(w)
            w = tha.ordinals.processor(w)
        words[j] = w.replace("▁", " ")

    # retokenize again after standardize
    ll = []
    j = 0
    while j < len(words):
        if words[j] == 'ចិត' and words[j+1] == 'សិប':
            ll.append('ចិតសិប')
            j += 1
        elif words[j] != ' ':
            ll.append(words[j])
        elif words[j] == '?':
            ll[j-1] += '?'
        j += 1
    transcription = "".join(ll)
    #transcription = word_tokenize(ds["transcription"], return_tokens=False, separator=" ")
    return {"transcription": transcription}
