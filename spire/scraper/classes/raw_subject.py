from spire.models import Subject
from spire.patterns import SUBJECT_ID_REGEXP, SUBJECT_TITLE_REGEXP
from spire.scraper.classes.shared import RawField, RawObject, clean_id, key_override_factory

SUBJECT_OVERRIDES = key_override_factory(
    {
        "BDIC": ("BDIC", "Bachelors Degree with Individualized Concentration"),
        "BIOCHEM": ("BIOCHEM", "Biochemistry & Molecular Biology"),
        "BIOST&EP": ("BIOSTEP", "Biostats & Epidemiology"),
        "BMED-ENG": ("BME", "Biomedical Engineering"),
        "CE-ENGIN": ("CEE", "Civil and Environmental Engineering"),
        "CHEM-ENG": ("CHE", "Chemical Engineering"),
        "CICS": ("CICS", "Manning College of Information & Computer Sciences"),
        ("EC-ENG", "E&C-ENG"): ("ECE", "Electrical & Computer Engineering"),
        ("HM&FN", "HMFNART", "HM&FNART"): ("HFA", "Humanities and Fine Arts"),
        "HT-MGT": ("HTM", "Hospitality & Tourism Management"),
        "LLEIP": ("LLIEP", "LL: Intensive English Program"),
        "LLSR&O": ("LLSRO", "LL: Sports, Recreation, and Outdoors"),
        ("MI-ENG", "M&I-ENG"): ("MIE", "Mechanical & Industrial Engineering"),
        ("NEUROS&B", "NEUROSB"): ("NSB", "Neuroscience & Behavior"),
        ("ORG&EVBI", "ORGEVBI"): ("OEB", "Organismic & Evolutionary Biology"),
        "PUBP&ADM": ("SPP", "School of Public Policy"),
        "SC@MIC": ("SC@MIC", "Science @ Mt. Ida College"),
        "SPHH": ("SPHH", "School of Public Health & Health Sciences"),
        "STOCKSCH": ("STOCKSCH", "Stockbridge School of Agriculture"),
        "ZEROCRED": ("TSTOCRED", "Zero Credit Test Equiv"),
    },
    as_table=True,
)


class RawSubject(RawObject):
    id: str
    title: str

    def __init__(self, id: str, title: str) -> None:
        id = clean_id(id)

        if id in SUBJECT_OVERRIDES:
            override = SUBJECT_OVERRIDES[id]

            self.id = override[0]
            self.title = override[1]
        else:
            self.id = id
            self.title = title

        super().__init__(
            Subject,
            fields=[
                RawField(k="id", re=SUBJECT_ID_REGEXP),
                RawField(k="title", re=SUBJECT_TITLE_REGEXP),
            ],
        )
