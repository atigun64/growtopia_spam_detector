from generator import GrammarGenerator
from grammars.positive import install_positive_spam_grammar
from grammars.negative import install_negative_spam_grammar

def main():
    gen = GrammarGenerator()
    install_positive_spam_grammar(gen)
    install_negative_spam_grammar(gen)
    # Generate some spam messages
    for _ in range(100):
        print(gen.generate("{SPAM_MESSAGE}"))


if __name__ == "__main__":
    main()