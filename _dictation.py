from dragonfly import *
import mode

grammar = Grammar("dictation")

dictation_lengths = []

def do_dictation(dictation):
    text = str(dictation)
    Text(text).execute()
    dictation_lengths.append(len(text))

def do_formatted_dictation(dictation):
    formatted_output = str(dictation)
    formatted_output += ' '
    Text(formatted_output).execute()
    dictation_lengths.append(len(formatted_output))

def undo_dictation():
    if dictation_lengths:
        Key("backspace:" + str(dictation_lengths.pop())).execute()

class DictationCommandRule(MappingRule):
    mapping = {
        "(dictate | say) <dictation> [over]":   Function(lambda dictation: do_dictation(dictation)),
        "(dictate | say) capital <dictation> [over]":   Function(lambda dictation: do_dictation(dictation.capitalize())),
        "retry (dictate | say) <dictation> [over]":   Function(undo_dictation) + Function(lambda dictation: do_dictation(dictation)),
        "undo (dictate | dictation)": Function(undo_dictation),
        "action dictation mode": Function(lambda: dictation_mode.pump()),
        # "splat":Key("c-backspace"),
        # "strike [<n>]":  Function(undo_dictation) * Repeat(extra='n'),
    }
    extras = [ Dictation("dictation") ]
    # extras = [ IntegerRef("n", 1, 10) ]
    # defaults = { "n": 1 }
grammar.add_rule(DictationCommandRule())

# ADD PERSONAL SINGLE-WORD TERMS HERE...
personal_uni_terms = "Kaldi backend parsing cache optimize software"
# ADD PERSONAL MULTIPLE-WORD TERMS HERE...
personal_multi_terms = ["left and right", "up and down"]

class DictationTerminologyRule(MappingRule):
    mapping = {
        # "kaldi": Text("Kaldi "),
        "<term>": Text("%(term)s "),
    }
    extras = [
        Choice("term", { t.lower(): t for t in (personal_uni_terms.split() + personal_multi_terms) }),
    ]
    exported = False
    # weight = 2

class FormattedDictationRule(MappingRule):
    mapping = {
        "<dictation>": Function(do_formatted_dictation),
    }
    extras = [ Dictation("dictation") ]
    exported = False
    # weight = 0.5

class SequenceRule(CompoundRule):
    spec = "<dict_cmd_sequence>"
    extras = [
        Repetition(Alternative([
            RuleRef(FormattedDictationRule()),
            RuleRef(DictationTerminologyRule()),
        ]), min=1, max=16, name="dict_cmd_sequence"),
    ]
    context = FuncContext(lambda: dictation_mode)
    def _process_recognition(self, node, extras):
        for action in extras["dict_cmd_sequence"]:
            action.execute()
grammar.add_rule(SequenceRule())

dictation_mode = mode.MultiMode(color='#f0f')

grammar.load()
