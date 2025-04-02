cd ner_model

huggingface-cli download dslim/bert-base-NER --local-dir . --local-dir-use-symlinks False

tar -czvf ../model.tar.gz * 

find . -mindepth 1 -maxdepth 1 ! -name 'code' -exec rm -rf {} +
