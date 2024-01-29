from flask import Flask, request, jsonify, g
from cltk import NLP
from cltk.alphabet.lat import normalize_lat
from flask_cors import CORS, cross_origin

def analyze_text(nlp: NLP, s: str):
    norm = normalize_lat(s, True, True, True, True)

    if g.get("cache") is None:
        g.cache = {}

    if norm in g.cache:
        return norm
    
    doc = nlp.analyze(text=s)
    analysis = []

    for word in doc.words:
        analysis.append(
            {
                "parent": word.governor,
                "parentRelation": word.dependency_relation,
                "pos": str(word.pos) if word.pos else None,
                "word": word.string,
                "definition": word.definition,
                "lemma": word.lemma,
                "category": {
                    str(x[0]).lower(): [str(y) for y in x[1]]
                    for x in word.category.all()
                }
                "features": {
                    str(x[0]).lower(): [str(y) for y in x[1]]
                    for x in word.features.all()
                },
            }
        )

    g.cache[norm] = analysis

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
