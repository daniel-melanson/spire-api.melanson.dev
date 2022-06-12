def key_override_factory(table):
    for k in list(table.keys()):
        if isinstance(k, tuple):
            value = table[k]
            del table[k]

            for sub_k in k:
                table[sub_k] = value

    def overrider(x):
        return table[x] if x in table else x

    return overrider


SUBJECT_OVERRIDES = key_override_factory(
    {
        "BDIC": ("BDIC", "Bachelors Degree with Individualized Concentration"),
        "BMED-ENG": ("BME", "Biomedical Engineering"),
        "CE-ENGIN": ("CEE", "Civil and Environmental Engineering"),
        "CHEM-ENG": ("CHE", "Chemical Engineering"),
        ("EC-ENG", "E&C-ENG"): ("ECE", "Electrical & Computer Engineering"),
        ("HM&FN", "HMFNART"): ("HFA", "Humanities and Fine Arts"),
        "HT-MGT": ("HTM", "Hospitality & Tourism Management"),
        ("MI-ENG", "M&I-ENG"): ("MIE", "Mechanical & Industrial Engineering"),
        ("NEUROS&B", "NEUROSB"): ("NSB", "Neuroscience & Behavior"),
        ("ORG&EVBI", "ORGEVBI"): ("OEB", "Organismic & Evolutionary Biology"),
    }
)


DETAIL_OVERRIDES = {
    "Academic Group": key_override_factory(
        {
            "College of Humanities&Fine Art": "College of Humanities & Fine Art",
            "Stockbridge School": "Stockbridge School of Agriculture",
            "College of Social & Behav. Sci": "College of Social & Behavioral Sciences",
        }
    ),
    "Academic Organization": key_override_factory(
        {
            "Bldg &Construction Technology": "Building & Construction Technology",
            "Civil & Environmental Engin.": "Civil & Environmental Engineering",
            "College of Info & Computer Sci": "Manning College of Information & Computer Sciences",
        }
    ),
    "Grading Basis": key_override_factory(
        {"Grad Ltr Grading, with options": "Graduate Letter Grading, with options"}
    ),
}
