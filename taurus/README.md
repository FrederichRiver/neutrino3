# Transformer

transformer library is built around three types of classes.

* Model class: like BertModel or GPT-2.  
* Config class: like BertConfig, to config models.  
* Tokenizer class: like BertTokenizer, which store vocabulary for each model and method to encoding/decoding strings for models.  

## NLP Task summary

* Sequence Classification  
* Extractive quetions answering  
* Language Modeling  
* Masked language modeling  
* Causal language modeling
* Text generation  
* Named entity recognition  
* Summarization  
* Translation  

## Named Entity Recognition

Named Entity Recognition (NER) is the task of classifying tokens according to a class, for example, identifying a token as a person, an organisation or a location. An example of a named entity recognition dataset is the CoNLL-2003 dataset, which is entirely based on that task. If you would like to fine-tune a model on an NER task, you may leverage the run_ner.py (PyTorch), run_pl_ner.py (leveraging pytorch-lightning) or the run_tf_ner.py (TensorFlow) scripts.

Here is an example of using pipelines to do named entity recognition, specifically, trying to identify tokens as belonging to one of 9 classes:

* O, Outside of a named entity
* B-MIS, Beginning of a miscellaneous entity right after another miscellaneous entity
* I-MIS, Miscellaneous entity
* B-PER, Beginning of a person’s name right after another person’s name
* I-PER, Person’s name
* B-ORG, Beginning of an organisation right after another organisation
* I-ORG, Organisation
* B-LOC, Beginning of a location right after another location
* I-LOC, Location

It leverages a fine-tuned model on CoNLL-2003, fine-tuned by @stefan-it from dbmdz.
```
>>> from transformers import pipeline

>>> nlp = pipeline("ner")

>>> sequence = "Hugging Face Inc. is a company based in New York City. Its headquarters are in DUMBO, therefore very"
...            "close to the Manhattan Bridge which is visible from the window."
```
This outputs a list of all words that have been identified as one of the entities from the 9 classes defined above. Here are the expected results:

```
>>> print(nlp(sequence))
[
    {'word': 'Hu', 'score': 0.9995632767677307, 'entity': 'I-ORG'},
    {'word': '##gging', 'score': 0.9915938973426819, 'entity': 'I-ORG'},
    {'word': 'Face', 'score': 0.9982671737670898, 'entity': 'I-ORG'},
    {'word': 'Inc', 'score': 0.9994403719902039, 'entity': 'I-ORG'},
    {'word': 'New', 'score': 0.9994346499443054, 'entity': 'I-LOC'},
    {'word': 'York', 'score': 0.9993270635604858, 'entity': 'I-LOC'},
    {'word': 'City', 'score': 0.9993864893913269, 'entity': 'I-LOC'},
    {'word': 'D', 'score': 0.9825621843338013, 'entity': 'I-LOC'},
    {'word': '##UM', 'score': 0.936983048915863, 'entity': 'I-LOC'},
    {'word': '##BO', 'score': 0.8987102508544922, 'entity': 'I-LOC'},
    {'word': 'Manhattan', 'score': 0.9758241176605225, 'entity': 'I-LOC'},
    {'word': 'Bridge', 'score': 0.990249514579773, 'entity': 'I-LOC'}
]
```

Note, how the tokens of the sequence “Hugging Face” have been identified as an organisation, and “New York City”, “DUMBO” and “Manhattan Bridge” have been identified as locations.

Here is an example of doing named entity recognition, using a model and a tokenizer. The process is the following:

1. Instantiate a tokenizer and a model from the checkpoint name. The model is identified as a BERT model and loads it with the weights stored in the checkpoint.

2. Define the label list with which the model was trained on.

3. Define a sequence with known entities, such as “Hugging Face” as an organisation and “New York City” as a location.

4. Split words into tokens so that they can be mapped to predictions. We use a small hack by, first, completely encoding and decoding the sequence, so that we’re left with a string that contains the special tokens.

5. Encode that sequence into IDs (special tokens are added automatically).

6. Retrieve the predictions by passing the input to the model and getting the first output. This results in a distribution over the 9 possible classes for each token. We take the argmax to retrieve the most likely class for each token.

7. Zip together each token with its prediction and print it.

```
PyTorch Code
>>> from transformers import AutoModelForTokenClassification, AutoTokenizer
>>> import torch

>>> model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
>>> tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

>>> label_list = [
...     "O",       # Outside of a named entity
...     "B-MISC",  # Beginning of a miscellaneous entity right after another miscellaneous entity
...     "I-MISC",  # Miscellaneous entity
...     "B-PER",   # Beginning of a person's name right after another person's name
...     "I-PER",   # Person's name
...     "B-ORG",   # Beginning of an organisation right after another organisation
...     "I-ORG",   # Organisation
...     "B-LOC",   # Beginning of a location right after another location
...     "I-LOC"    # Location
... ]

>>> sequence = "Hugging Face Inc. is a company based in New York City. Its headquarters are in DUMBO, therefore very" \
...            "close to the Manhattan Bridge."

>>> # Bit of a hack to get the tokens with the special tokens
>>> tokens = tokenizer.tokenize(tokenizer.decode(tokenizer.encode(sequence)))
>>> inputs = tokenizer.encode(sequence, return_tensors="pt")

>>> outputs = model(inputs).logits
>>> predictions = torch.argmax(outputs, dim=2)
```

This outputs a list of each token mapped to its corresponding prediction. Differently from the pipeline, here every token has a prediction as we didn’t remove the “0”th class, which means that no particular entity was found on that token. The following array should be the output:
```
>>> print([(token, label_list[prediction]) for token, prediction in zip(tokens, predictions[0].numpy())])
[('[CLS]', 'O'), ('Hu', 'I-ORG'), ('##gging', 'I-ORG'), ('Face', 'I-ORG'), ('Inc', 'I-ORG'), ('.', 'O'), ('is', 'O'), ('a', 'O'), ('company', 'O'), ('based', 'O'), ('in', 'O'), ('New', 'I-LOC'), ('York', 'I-LOC'), ('City', 'I-LOC'), ('.', 'O'), ('Its', 'O'), ('headquarters', 'O'), ('are', 'O'), ('in', 'O'), ('D', 'I-LOC'), ('##UM', 'I-LOC'), ('##BO', 'I-LOC'), (',', 'O'), ('therefore', 'O'), ('very', 'O'), ('##c', 'O'), ('##lose', 'O'), ('to', 'O'), ('the', 'O'), ('Manhattan', 'I-LOC'), ('Bridge', 'I-LOC'), ('.', 'O'), ('[SEP]', 'O')]
```

