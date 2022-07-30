import random
import json
import requests

def alter_sentence(sentence, options={
    "scramble" : True,
    "swap" : True, # swap word positions
    "synonyms" : True, # swap words with synonyms
}):

    sentence: list = sentence.split()
    out: list = sentence.copy()

    # check options 
    if options["scramble"]:
        word_index = random.randint(0, len(sentence) - 1)
        word = list(sentence[word_index])

        if len(word) > 2: # word has to be at least 3 letters long
            shuffled = word.copy()[1:-1]
            random.shuffle(shuffled)
            # re-add the first and last letters
            shuffled.append(word[-1])
            shuffled.insert(0, word[0])
            out[word_index] = "".join(shuffled)


    if options["swap"]:
        # choose two random indexes of the sentence to swap
        indexs = [random.randint(0, len(sentence) - 1), random.randint(0, len(sentence) - 1)]

        out[indexs[0]] = sentence[indexs[1]]
        out[indexs[1]] = sentence[indexs[0]]

    if options["synonyms"]:
        word_index = random.randint(0, len(sentence) - 1)
        # caps at 500 requests per day
        req = requests.get(f"https://words.bighugelabs.com/api/2/1e5ba04c55a9223c4433a43de00f8137/{sentence[word_index]}/json")
        try:
            req = req.json()
            out[word_index ] = random.choice(req[random.choice(list(req.keys()))]["syn"])
        # no synonyms or invalid word
        except (json.decoder.JSONDecodeError, KeyError):
            print("Error: No synonyms found for word or API is used up")
            pass
            
        
    # concatenate the sentence
    return " ".join(out)

print(alter_sentence("I am a sentence"))
print(alter_sentence("I am a sentence with some long words such as gregariousness"))