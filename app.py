from cltk.core import Word
from flask import Flask, request, jsonify, g
from cltk import NLP
from cltk.dependency.tree import DependencyTree
from cltk.tokenizers.processes import LatinTokenizationProcess
from cltk.lemmatize.processes import LatinLemmatizationProcess
from cltk.alphabet.lat import normalize_lat
from pywords.lookup import match_word, get_dictionary_string
from flask_cors import CORS, cross_origin
from pprint import pprint


def generate_sd(doc, words):
    s = " ".join([f"{word.string}/{word.upos}" for word in words]) + "\n"
    for word in words:
        if str(word.pos) == "ROOT":
            continue

        s += f"{word.dependency_relation}({word.string}-{word.index_token}, {next(x for x in doc.words if x.index_token == word.governor).string}-{word.governor})\n"

    return s


def analyze_text(nlp: NLP, s: str):
    s = s.replace("\r\n", " ").replace("\n", " ")
    norm = normalize_lat(s, True, True, False, True)
    norm2 = normalize_lat(s, True, True, True, True)
    print(norm)

    if g.get("cache") is None:
        g.cache = {}

    if norm2 in g.cache:
        return g.cache[norm2]

    doc = nlp.analyze(text=norm)
    analysis = []
    print(doc.tokens)
    for word in doc.words:
        # print(word.governor)
        # print(f"{word.string} {word.index_token}")
        analysis.append(
            {
                "index": word.index_token,
                "parent": word.governor,
                "parentRelation": word.dependency_relation,
                "xpos": str(word.xpos) if word.xpos else None,
                "upos": str(word.upos) if word.upos else None,
                "pos": str(word.pos) if word.pos else None,
                "word": word.string,
                "definition": "\n===========\n".join(
                    [get_dictionary_string(m, False) for m in match_word(word.lemma.lower())]
                ),
                "definition_long": word.definition,
                "lemma": word.lemma,
                "category": {
                    str(x[0]).lower(): [str(y) for y in x[1]]
                    for x in word.category.all()
                },
                "features": {
                    str(x[0]).lower(): [str(y) for y in x[1]]
                    for x in word.features.all()
                },
            }
        )

    print(generate_sd(doc, doc.sentences[0].words))
    print(generate_sd(doc, [*doc.sentences[0].words, *doc.sentences[1].words]))

    g.cache[norm2] = analysis
    tree = DependencyTree.to_tree(doc.sentences[0].words)
    pprint(tree.get_dependencies())

    return analysis


t = """
Avunculus meus Mīsēnī erat classis praefectus. Eō diē, quō tantae
clādis initium fuit, avunculus forīs iacēbat librīsque studēbat. Māter
mea eī nūbem subitō ostendit novam et inūsitātam, quae in caelō prope
montem Vesuvium vidēbātur esse. Nūbēs fōrmam habuit similem
fōrmae, quam in arboribus saepe vidēmus. Nam summa nūbēs in
multās partēs sīcut in rāmōs sēparābātur. Avunculus, homō rērum
nātūrae valdē studiōsus, causam nūbis intellegere cupīvit. Iussit igitur
nāvēs parārī: nam ad lītus nāvigāre cupīvit, quod est prope montem
Vesuvium. Deinde nauta epistulam avunculō dedit. “Fēmina,” inquit
nauta, “quae prope montem Vesuvium habitat, epistulam ad tē mīsit.”
Avunculus epistulam lēgit et statim intellēxit in monte Vesuviō esse
incendium magnum: fēminam perīculum timēre nāvibusque fugere
cupere. Animus fortis avunculō erat. Cōnsilium igitur novum cēpit. Ad
hominēs nāvigāre dēcrēvit, quī prope montem Vesuvium habitābant, et
eōs perīculō magnō līberāre. Nam saxa et cinerēs calidī ē caelō in eōs
cadēbant. Illūc igitur nāvigāvit, sed numquam revēnit. Ibi enim fūmus
fūnestus et cinerēs eum cum multīs aliīs oppressērunt."""

TEXT_MAX_LEN = 6666

app = Flask(__name__)
cors = CORS(app)
nlp = NLP(language="lat")

nlp.pipeline.processes.insert(1, LatinTokenizationProcess)
#nlp.pipeline.processes.insert(2, LatinLemmatizationProcess)

print(nlp.pipeline.processes)


@app.route("/")
def index():
    return "<p>Hello, World!</p>"


@app.route("/analyze", methods=["POST"])
@cross_origin()
def analyze():
    text = request.get_json().get("text")

    if text is None:
        return jsonify({"status": "error", "data": "No text submitted."})

    if len(text) > TEXT_MAX_LEN:
        return jsonify(
            {
                "status": "error",
                "data": f"You are exceeding the max text length of {TEXT_MAX_LEN}",
            }
        )

    return jsonify(analyze_text(nlp, text))


if __name__ == "__main__":
    app.run(threaded=True)
