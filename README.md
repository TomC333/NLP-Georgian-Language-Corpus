# NLP Georgian Language Corpus 🇬🇪

[![Build Status](https://img.shields.io/badge/build-success-green)](https://github.com/TomC333/NLP-Georgian-Language-Corpus)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/TomC333/NLP-Georgian-Language-Corpus/blob/main/LICENSE)
[![Dataset](https://img.shields.io/badge/dataset-HuggingFace-orange)](https://huggingface.co/datasets/TomC333/georgian-language-corpus)

## Background 📚

This project was part of a university assignment focused on natural language processing. At first glance, it might look like a typical scraping job — and honestly, it kind of is 😅. My main goal was to collect a clean set of Georgian language text from the Common Crawl dataset.

Turns out, scraping *Georgian* websites is an entirely different beast. I tried a ridiculous number of approaches to filter out non-Georgian content — regexes, language detection libraries, URL filtering... you name it. Unfortunately, none of them were truly effective. But hey, that’s the beauty of assignments, right? 😄

While the filters used in this code aren’t top-tier, they serve as a reference point for others who might want to attempt something similar. If you're exploring ways to build a Georgian language corpus, feel free to take a look, fork it, and make it better. Just don’t expect miracles from this version 😅.

## Dataset 📦

The resulting corpus is publicly available on Hugging Face:  
👉 [Hugging Face Dataset Link](https://huggingface.co/datasets/TomC333/georgian-language-corpus)  

It's not massive, and it's definitely not perfect — but it’s a starting point.

## Setup & Usage ⚙️

To run this project locally:

```bash
git clone https://github.com/Toms343/NLP-Georgian-Language-Corpus.git
cd NLP-Georgian-Language-Corpus
pip install -r requirements.txt
python crawl.py
