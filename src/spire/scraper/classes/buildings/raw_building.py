import logging
import re
from difflib import get_close_matches
from typing import Optional

from nltk import word_tokenize

from spire.models import Building, BuildingRoom
from spire.scraper.classes.shared import RawField, RawObject, key_override_factory, re_override_factory
from spire.scraper.web import clean_text

log = logging.getLogger(__name__)


class RawBuilding(RawObject):
    def __init__(self, name: str, address: Optional[str]) -> None:
        self.name = name
        self.address = address

        super().__init__(Building, None, [RawField("name"), RawField("address")])

    def push(self):
        obj, _ = Building.objects.get_or_create(name=self.name)

        return obj


class RawBuildingRoom(RawObject):
    def __init__(self, building=None, number=None, alt=None) -> None:
        self.building = building
        self.number = number
        self.alt = alt

        super().__init__(BuildingRoom, None, [RawField("building"), RawField("number"), RawField("alt")])

    def push(self):
        if self.building:
            building = self.building.push()
            log.debug("Pushed building: %s", building)
            try:
                b = BuildingRoom.objects.get(alt=self.alt)

                log.debug("Found building room: %s", b)

                assert b.building == building
                assert b.number == self.number
            except BuildingRoom.DoesNotExist:
                b, _ = BuildingRoom.objects.get_or_create(
                    building=building, number=self.number, defaults={"alt": self.alt}
                )

            return b
        else:
            b, _ = BuildingRoom.objects.get_or_create(alt=self.alt)

        return b


BUILDINGS = [
    RawBuilding(
        name="Agricultural Engineering Building",
        address="250 Natural Resources Rd, Amherst, MA 01003-9295",
    ),
    RawBuilding(
        name="Agricultural Experiment Station", address="160 Tillson Farm Rd, Amherst, MA 01003-9346"
    ),
    RawBuilding(
        name="Army ROTC Building",
        address="101 Commonwealth Ave, Amherst, MA 01003-9252",
    ),
    RawBuilding(
        name="Arnold House",
        address="715 N Pleasant, Amherst, MA 01003-9304",
    ),
    RawBuilding(
        name="Auxiliary Services Warehouse",
        address="31 Cold Storage Dr, Amherst, MA 01003-9344",
    ),
    RawBuilding(
        name="Baker Hall",
        address="160 Clark Hill Rd, Amherst, MA 01003-9205",
    ),
    RawBuilding(
        name="Baker House",
        address="160 Clark Hill Rd Ofc, Amherst, MA 01003-9321",
    ),
    RawBuilding(
        name="Bartlett Hall",
        address="130 Hicks Way, Amherst, MA 01003-9269",
    ),
    RawBuilding(
        name="Berkshire Dining Common",
        address="121 Southwest Cir, Amherst, MA 01003-9314",
    ),
    RawBuilding(
        name="Berkshire House",
        address="121 County Cir, Amherst, MA 01003-9256",
    ),
    RawBuilding(
        name="Birch Hall",
        address="153 Commonwealth Ave, Amherst, MA 01003-9253",
    ),
    RawBuilding(name="Blaisdell House", address="113 Grinnell Way, Amherst, MA 01003-9367"),
    RawBuilding(name="Boulder House Mt Ida Campus", address="97 Carlson Ave, Newton, MA 02459-3307"),
    RawBuilding(name="Bowditch Hall", address="201 Natural Resources Rd, Amherst, MA 01003-9294"),
    RawBuilding(name="Bowditch Lodge", address="31 Clubhouse Dr, Amherst, MA 01003-9250"),
    RawBuilding(name="Boyden Gym", address="131 Commonwealth Ave, Amherst, MA 01003-9253"),
    RawBuilding(name="Brett Hall", address="151 Infirmary Way Ofc, Amherst, MA 01003-9322"),
    RawBuilding(name="Brett Hall", address="151 Infirmary Way, Amherst, MA 01003-9219"),
    RawBuilding(name="Brooks Hall", address="160 Infirmary Way, Amherst, MA 01003-9200"),
    RawBuilding(name="Brown Hall", address="92 Eastman Ln, Amherst, MA 01003-9210"),
    RawBuilding(name="Butterfield Hall", address="171 Clark Hill Rd, Amherst, MA 01003-9206"),
    RawBuilding(name="Campus Center", address="1 Campus Center Way, Amherst, MA 01003-9243"),
    RawBuilding(name="Cance Hall", address="191 Fearing Ofc, Amherst, MA 01003-9323"),
    RawBuilding(name="Cance Hall", address="191 Fearing St, Amherst, MA 01003-9218"),
    RawBuilding(name="Cashin Hall", address="112 Eastman Ln, Amherst, MA 01003-9220"),
    RawBuilding(name="Central Heating Plant", address="200 Mullins Way, Amherst, MA 01003-9352"),
    RawBuilding(name="Chadbourne Hall", address="110 Orchard Hill Dr, Amherst, MA 01003-9207"),
    RawBuilding(name="Champions Center", address="190 Commonwealth Ave, Amherst, MA 01003-9398"),
    RawBuilding(name="Chancellor's House", address="150 Chancellors Dr, Amherst, MA 01003-9249"),
    RawBuilding(name="Chenoweth Laboratory", address="100 Holdsworth Way, Amherst, MA 01003-9282"),
    RawBuilding(name="Clark Hall", address="251 Stockbridge Rd, Amherst, MA 01003-9319"),
    RawBuilding(name="Commonwealth Honors College", address="157 Commonwealth Ave, Amherst, MA 01003-9253"),
    RawBuilding(name="Communication Disorders Building", address="358 N Pleasant St, Amherst, MA 01003-9296"),
    RawBuilding(name="Computer Science Building", address="140 Governors Dr, Amherst, MA 01003-9264"),
    RawBuilding(
        name="Condensate Storage Building", address="30 Campus Center Service Rd, Amherst, MA 01003-9244"
    ),
    RawBuilding(name="Conte Polymer Center", address="120 Governors Dr, Amherst, MA 01003-9263"),
    RawBuilding(name="Coolidge Hall", address="630 Massachusetts Ave, Amherst, MA 01003-9239"),
    RawBuilding(name="Crabtree Hall", address="17 Eastman Ln, Amherst, MA 01003-9226"),
    RawBuilding(name="Crampton Hall", address="256 Sunset Ave, Amherst, MA 01003-9232"),
    RawBuilding(name="Crotty Hall", address="412 N Pleasant St, Amherst, MA 01002-2900"),
    RawBuilding(name="Curry Hicks Gym", address="100 Hicks Way, Amherst, MA 01003-9267"),
    RawBuilding(name="Dickinson Hall", address="155 Hicks Way, Amherst, MA 01003-9363"),
    RawBuilding(name="Dickinson Dorm", address="151 Orchard Hill Dr, Amherst, MA 01003-9222"),
    RawBuilding(name="Draper Hall", address="40 Campus Center Way, Amherst, MA 01003-9244"),
    RawBuilding(name="Dwight Hall", address="41 Eastman Ln, Amherst, MA 01003-9228"),
    RawBuilding(name="East Experiment Station", address="671 N Pleasant St, Amherst, MA 01003-9301"),
    RawBuilding(name="Elm Hall", address="145 Commonwealth Ave, Amherst, MA 01003-9253"),
    RawBuilding(name="Emerson Hall", address="151 Southwest Cir, Amherst, MA 01003-9237"),
    RawBuilding(name="Engineering Laboratory", address="160 Governors Dr, Amherst, MA 01003-9265"),
    RawBuilding(name="Engineering Laboratory II", address="101 North Service Rd, Amherst, MA 01003-9345"),
    RawBuilding(name="Faculty Club", address="243 Stockbridge Rd, Amherst, MA 01003-9317"),
    RawBuilding(name="Farley Lodge", address="41 Clubhouse Dr, Amherst, MA 01003-9251"),
    RawBuilding(name="Fernald Hall", address="270 Stockbridge Rd, Amherst, MA 01003-9320"),
    RawBuilding(name="Field Hall", address="171 Orchard Hill Dr, Amherst, MA 01003-9225"),
    RawBuilding(
        name="Bromery Center for Art",
        address="151 Presidents, Amherst, MA 01003-9330",
    ),
    RawBuilding(name="Flint Laboratory", address="90 Campus Center Way, Amherst, MA 01003-9247"),
    RawBuilding(name="Football Performance Center", address="290 Stadium Dr, Amherst, MA 01003-9397"),
    RawBuilding(name="Franklin Dining Common", address="260 Stockbridge Rd, Amherst, MA 01003-9314"),
    RawBuilding(name="French Hall", address="230 Stockbridge Rd, Amherst, MA 01003-9316"),
    RawBuilding(name="Furcolo Hall", address="813 N Pleasant St, Amherst, MA 01003-9308"),
    RawBuilding(name="Goessmann Laboratory", address="686 N Pleasant St, Amherst, MA 01003-9303"),
    RawBuilding(name="Goodell Building", address="140 Hicks Way, Amherst, MA 01003-9272"),
    RawBuilding(name="Gordon Hall", address="418 N Pleasant St, Amherst, MA 01002-1735"),
    RawBuilding(name="Gorman Hall", address="90 Butterfield Ter, Amherst, MA 01003-9202"),
    RawBuilding(name="Grayson Hall", address="161 Orchard Hill Dr, Amherst, MA 01003-9221"),
    RawBuilding(name="Grinnell Arena", address=None),
    RawBuilding(name="Greenough Hall", address="120 Orchard Hill Dr, Amherst, MA 01003-9224"),
    RawBuilding(name="Gunness Laboratory", address="121 Natural Resources Rd, Amherst, MA 01003"),
    RawBuilding(name="Hamlin Hall", address="739 N Pleasant St, Amherst, MA 01003-9211"),
    RawBuilding(name="Hampden Dining Common", address="131 Southwest Cir, Amherst, MA 01003-9314"),
    RawBuilding(name="Hampshire Dining Common", address="141 Southwest Cir, Amherst, MA 01003-9314"),
    RawBuilding(name="Hampshire House", address="131 County Cir, Amherst, MA 01003-9257"),
    RawBuilding(name="Hasbrouck Laboratory", address="666 N Pleasant St, Amherst, MA 01003-9300"),
    RawBuilding(name="Hatch Laboratory", address="140 Holdsworth Way, Amherst, MA 01003-9283"),
    RawBuilding(name="Herter Hall", address="161 Presidents Dr, Amherst, MA 01003-9312"),
    RawBuilding(name="Hillel House", address="388 N Pleasant St #15, Amherst, MA 01002-1753"),
    RawBuilding(name="Holdsworth Hall", address="160 Holdsworth Way, Amherst, MA 01003-9285"),
    RawBuilding(name="Institute for Holocaust", address="758 N Pleasant St, Amherst, MA 01002-1310"),
    RawBuilding(name="Integrated Sciences Building", address="661 N Pleasant St, Amherst, MA 01003-9301"),
    RawBuilding(name="Integrative Learning Center", address="650 N Pleasant St, Amherst, MA 01003-1100"),
    RawBuilding(name="International Programs", address="70 Butterfield Terr, Amherst, MA 01003-9242"),
    RawBuilding(name="Isenberg School of Management", address="121 Presidents Dr, Amherst, MA 01003-9310"),
    RawBuilding(name="James Hall", address="660 Massachusetts Ave, Amherst, MA 01003-9217"),
    RawBuilding(name="John Adams Hall", address="161 Fearing St, Amherst, MA 01003-9234"),
    RawBuilding(name="John Quincy Adams Hall", address="171 Fearing St, Amherst, MA 01003-9235"),
    RawBuilding(name="John Quincy Adams Tower", address="171 Fearing St Ofc, Amherst, MA 01003-9325"),
    RawBuilding(name="Johnson Hall", address="380 Thatcher Rd, Amherst, MA 01003-9359"),
    RawBuilding(name="Johnson House", address="380 Thatcher Rd Ofc, Amherst, MA 01003-9359"),
    RawBuilding(name="Kennedy Hall", address="620 Massachusetts Ave, Amherst, MA 01003-9238"),
    RawBuilding(name="Knowles Engineering Building", address="151 Holdsworth Way, Amherst, MA 01003-9284"),
    RawBuilding(name="Knowlton Hall", address="691 N Pleasant St Ofc, Amherst, MA 01003-9399"),
    RawBuilding(name="Knowlton Hall", address="691 N Pleasant St, Amherst, MA 01003-9212"),
    RawBuilding(name="Leach Hall", address="21 Eastman Ln, Amherst, MA 01003-9227"),
    RawBuilding(name="Lederle Grad Research Center", address="740 N Pleasant St, Amherst, MA 01003-9306"),
    RawBuilding(name="Lederle Grad Research Tower", address="710 N Pleasant St, Amherst, MA 01003-9305"),
    RawBuilding(name="Lewis Hall", address="340 Thatcher Rd, Amherst, MA 01003-9359"),
    RawBuilding(name="Life Science Laboratories", address="240 Thatcher Rd, Amherst, MA 01003-9364"),
    RawBuilding(name="Lincoln Apts", address="345 Lincoln Ave, Amherst, MA 01003-9373"),
    RawBuilding(name="Linden Hall", address="141 Commonwealth Ave, Amherst, MA 01003-9253"),
    RawBuilding(name="Machmer Hall", address="240 Hicks Way, Amherst, MA 01003-9278"),
    RawBuilding(name="Mackimmie Hall", address="230 Sunset Ave, Amherst, MA 01003-9231"),
    RawBuilding(name="Maple Hall", address="151 Commonwealth Ave, Amherst, MA 01003-9253"),
    RawBuilding(name="Marcus Hall", address="100 Natural Resources Rd, Amherst, MA 01003-9292"),
    RawBuilding(name="Marston Hall", address="130 Natural Resources Rd, Amherst, MA 01003-9293"),
    RawBuilding(name="Mary Lyon Hall", address="43 Eastman Ln, Amherst, MA 01003-9208"),
    RawBuilding(name="Mass Ventures", address="100 Venture Way, Hadley, MA 01035-9462"),
    RawBuilding(name="Mather Building", address="37 Mather Dr, Amherst, MA 01003-9291"),
    RawBuilding(name="McNamara Hall", address="102 Eastman Ln, Amherst, MA 01003-9203"),
    RawBuilding(name="Melville Hall", address="650 Massachusetts Ave, Amherst, MA 01003-9241"),
    RawBuilding(name="Memorial Hall", address="134 Hicks Way, Amherst, MA 01003-9270"),
    RawBuilding(name="Middlesex House", address="111 County Cir, Amherst, MA 01003-9255"),
    RawBuilding(name="Montague House", address="809 N Pleasant St, Amherst, MA 01003-9307"),
    RawBuilding(name="Moore Hall", address="111 Southwest Cir, Amherst, MA 01003-9216"),
    RawBuilding(name="Morrill Science Center 1", address="637 N Pleasant St, Amherst, MA 01003-9298"),
    RawBuilding(name="Morrill Science Center 2", address="627 N Pleasant St, Amherst, MA 01003-9354"),
    RawBuilding(name="Morrill Science Center 3", address="611 N Pleasant St, Amherst, MA 01003-9297"),
    RawBuilding(name="Morrill Science Center 4", address="639 N Pleasant St, Amherst, MA 01003-9298"),
    RawBuilding(name="Mount Ida Campus", address="100 Carlson Avenue, Newton, MA 02459-3310"),
    RawBuilding(name="Mullins Center", address="200 Commonwealth Ave, Amherst, MA 01003-9254"),
    RawBuilding(name="Munson Hall", address="101 Hicks Way, Amherst, MA 01003-9268"),
    RawBuilding(name="Nelson House", address="513 East Pleasant St, Amherst, MA 01003-9260"),
    RawBuilding(name="Nelson House South", address="505 East Pleasant St, Amherst, MA 01003-9259"),
    RawBuilding(name="New Africa House", address="180 Infirmary Way, Amherst, MA 01003-9289"),
    RawBuilding(name="North Residence A", address="56 Eastman Ln, Amherst, MA 01003-9350"),
    RawBuilding(name="North Residence B", address="58 Eastman Ln, Amherst, MA 01003-9351"),
    RawBuilding(name="North Residence C", address="54 Eastman Ln, Amherst, MA 01003-9349"),
    RawBuilding(name="North Residence D", address="52 Eastman Ln, Amherst, MA 01003-9348"),
    RawBuilding(name="North Village Apts.", address="990 N Pleasant St, Amherst, MA 01002"),
    RawBuilding(name="Oak Hall", address="143 Commonwealth Ave, Amherst, MA 01003-9253"),
    RawBuilding(name="Old Chapel", address="144 Hicks Way, Amherst, MA 01003-9273"),
    RawBuilding(name="Olver Design Building", address="551 N Pleasant St, Amherst, MA 01003-2901"),
    RawBuilding(name="Online Education UWW", address="350 Campus Center Way, Amherst, MA 01003-2902"),
    RawBuilding(name="Paige Laboratory", address="161 Holdsworth Way, Amherst, MA 01003-9286"),
    RawBuilding(name="Parking Office Trailer", address="51 Forestry Way, Amherst, MA 01003-9262"),
    RawBuilding(name="Parks Marching Band Building", address="110 Grinnell Way, Amherst, MA 01003-9365"),
    RawBuilding(name="Patterson Hall", address="204 Sunset Ave, Amherst, MA 01003-9213"),
    RawBuilding(name="Photo Center", address="211 Hicks Way, Amherst, MA 01003-9372"),
    RawBuilding(name="Physical Plant", address="360 Campus Center Way, Amherst, MA 01003-9248"),
    RawBuilding(name="Physical Sciences Building", address="690 N Pleasant St, Amherst, MA 01003-9303"),
    RawBuilding(name="Pierpont Hall", address="201 Fearing St, Amherst, MA 01003-9215"),
    RawBuilding(name="Police Station", address="585 East Pleasant St, Amherst, MA 01003-9600"),
    RawBuilding(name="Prince Hall", address="286 Sunset Ave, Amherst, MA 01003-9233"),
    RawBuilding(name="Recreation Center", address="161 Commonwealth Ave, Amherst, MA 01003-9253"),
    RawBuilding(name="Renaissance Center", address="650 E Pleasant St, Amherst, MA 01002-1526"),
    RawBuilding(name="Robsham Visitor's Center", address="300 Massachusetts Ave, Amherst, MA 01003-9290"),
    RawBuilding(name="Shade Trees Laboratory", address="245 Stockbridge Rd, Amherst, MA 01003-9318"),
    RawBuilding(name="Skinner Hall", address="651 N Pleasant St, Amherst, MA 01003-9299"),
    RawBuilding(name="Slobody Building", address="101 University Dr Suite B, Amherst, MA 01002-2376"),
    RawBuilding(name="South College", address="150 Hicks Way, Amherst, MA 01003-9274"),
    RawBuilding(name="Stockbridge Hall", address="80 Campus Center Way, Amherst, MA 01003-9246"),
    RawBuilding(name="Stonewall Center", address="256 Sunset Ave Ofc, Amherst, MA 01003-9232"),
    RawBuilding(name="Student Union", address="41 Campus Center Way, Amherst, MA 01003-9245"),
    RawBuilding(name="Studio Arts Building", address="110 Thatcher Rd, Amherst, MA 01003-9356"),
    RawBuilding(name="Sycamore Hall", address="159 Commonwealth Ave, Amherst, MA 01003-9253"),
    RawBuilding(name="Thatcher Hall", address="300 Thatcher Rd, Amherst, MA 01003-9359"),
    RawBuilding(name="Thompson Hall", address="200 Hicks Way, Amherst, MA 01003-9277"),
    RawBuilding(name="Thoreau Hall", address="640 Massachusetts Ave, Amherst, MA 01003-9240"),
    RawBuilding(name="Thoreau House", address="640 Massachusetts Ave Ofc, Amherst, MA 01003-9327"),
    RawBuilding(name="Tillson Farm", address="151 Tillson Farm Rd, Amherst, MA 01003"),
    RawBuilding(name="Tillson House", address="23 Tillson Farm Rd, Amherst, MA 01003-9346"),
    RawBuilding(name="Tobin Hall", address="135 Hicks Way, Amherst, MA 01003-9271"),
    RawBuilding(name="Toddler House", address="21 Clubhouse Dr, Amherst, MA 01003-9343"),
    RawBuilding(name="Totman Gym", address="30 Eastman Ln, Amherst, MA 01003-9258"),
    RawBuilding(name="University Bus Garage", address="185 Holdsworth Way, Amherst, MA 01003-9286"),
    RawBuilding(name="University Health Services", address="150 Infirmary Way, Amherst, MA 01003-9288"),
    RawBuilding(name="University Press", address="671 N Pleasant St, Amherst, MA 01003-9301"),
    RawBuilding(name="University Store", address="1 Campus Center Way Ofc, Amherst, MA 01003-9332"),
    RawBuilding(
        name="University Without Walls UWW, Online Ed",
        address="350 Campus Center Way, Amherst, MA 01003-2902",
    ),
    RawBuilding(name="Van Meter Hall", address="180 Clark Hill Rd, Amherst, MA 01003-9223"),
    RawBuilding(name="W.E.B. Du Bois Library", address="154 Hicks Way, Amherst, MA 01003-9275"),
    RawBuilding(name="Washington Hall", address="181 Fearing St, Amherst, MA 01003-9236"),
    RawBuilding(name="Webster Hall", address="141 Orchard Hill Dr, Amherst, MA 01003-9204"),
    RawBuilding(name="West Experiment Station", address="682 N Pleasant St, Amherst, MA 01003-9302"),
    RawBuilding(name="Wheeler Hall", address="171 Infirmary Way, Amherst, MA 01003-9201"),
    RawBuilding(name="Whitmore Building", address="181 Presidents Dr, Amherst, MA 01003-9313"),
    RawBuilding(name="Wilder Hall", address="221 Stockbridge Rd, Amherst, MA 01003-9315"),
    RawBuilding(name="Worcester Commons", address="667 N Pleasant St, Amherst, MA 01003-9301"),
    RawBuilding(name="Wysocki House", address="911 N Pleasant St, Amherst, MA 01003-9309"),
    RawBuilding(name="UMass Memorial Medical Center", address="55 Lake Ave N, Worcester, MA 01655"),
    RawBuilding(name="UMass Amherst Center at Springfield", address="1500 Main St, Springfield, MA 01115"),
    RawBuilding(
        name="Springfield Technical Community College", address="1 Armory St, Unit 1, Springfield, MA 01105"
    ),
    RawBuilding(name="Mahar Auditorium", address="119 Presidents Dr, Amherst, MA 01002"),
    RawBuilding(
        name="Research and Education Greenhouse", address="246 Natural Resources Rd, Amherst, MA 01003"
    ),
]

BUILDINGS_DICT: dict[str, RawBuilding] = {b.name: b for b in BUILDINGS}

BUILDING_NAMES = [b.name for b in BUILDINGS]

BUILDING_NAME_SETS = [set(n.split(" ")) for n in BUILDING_NAMES]

ACCEPTED_BUILDING_POSTFIXES = (
    "Theater",
    "Plant",
    "Hall",
    "College",
    "Gym",
    "House",
    "Arena",
    "Auditorium",
    "Stage",
    "Lobby",
    "Center",
    "Pool",
    "@ Mount Ida",
)

ABBREVIATIONS = key_override_factory(
    ("ag", "Agricultural"),
    ("eng", "Engineering"),
    ("agengineering", "Agricultural Engineering"),
    ("engin", "Engineering"),
    ("bldg", "Building"),
    (("rm", "classroom", "rom"), "Room"),
    ("phys", "Physical"),
    (("ed", "educ"), "Education"),
    (("cntr", "ctr"), "Center"),
    ("fac", "Bromery Center for Art"),
    ("sch", "School"),
    ("sci", "Science"),
    ("res", "Research"),
    ("&", "and"),
    ("dubois", "Du Bois"),
    ("lrng", "Learning"),
    ("brkshre", "Berkshire"),
    ("dini", "Dining Hall"),
    ("lab", "Laboratory"),
    ("sprngfld", "Springfield"),
    ("seminarrm", "Seminar Room"),
    ("desgncntr-vermon", "Design Center Vermon"),
    ("loung", "Lounge"),
    ("addtn", "Addition"),
)

CONTEXTUAL_ABBREVIATIONS = [
    ("Laboratory Add", "Laboratory Addition"),
    ("Integ Learning", "Integrative Learning"),
    ("Center IV", "Center 4"),
    ("Center III", "Center 3"),
    ("Center II", "Center 2"),
    ("Center I", "Center 1"),
    ("Mt Ida", "Mount Ida"),
    ("@ MI", "@ Mount Ida"),
    ("MountIda", "Mount Ida"),
    ("Physical Education Building", "Gym"),
    ("Bromery Center", "Bromery Center for Art"),
    ("Comm College", "Community College"),
]

PATTERN_OVERRIDES = re_override_factory(
    (r"Morrill (\d|[IV]+)(.+)", "Morrill Science Center $1$2"),
    (r"Machmer ([A-Z]) - (\d{1,3})", "Machmer Hall room $1-$2"),
)

BUILDING_OVERRIDES = {
    "358 North Pleasant Street": "Communication Disorders Building",
}

BUILDING_MATCH_OVERRIDES = key_override_factory(
    ("Totman", "Totman Gym"),
    (("Library Tower", "Library Lower Level"), "W.E.B. Du Bois Library"),
    ("Goodell", "Goodell Building"),
    ("Grayson Dorm", "Grayson Hall"),
    ("Mahar", "Mahar Auditorium"),
    ("Morrill Science", "Morrill Scince Center 1"),
    ("Boyden", "Boyden Gym"),
    ("Integrated Sciences Laboratory", "Integrated Sciences Building"),
    ("Noah Webster House", "Webster Hall"),
    (("Furcolo W", "Furcolo Carney Fam Auditorium"), "Furcolo Hall"),
    ("George Parks Building", "Parks Marching Band Building"),
    ("Honors College Building", "Commonwealth Honors College Building"),
    (("Morrill Science Center 1 North", "Morrill Science"), "Morrill Science Center 1"),
)


def expand_text(s: str) -> str:
    log.debug("Expanding: %s", s)
    s = clean_text(s.replace(".", " "))

    kept = []
    for token in filter(lambda x: x not in (".", "(", ")"), word_tokenize(s)):

        token_l = token.lower()
        if len(token) >= 3 and token_l.startswith("rm") and token[2].isdigit():
            kept.append("Room")
            kept.append(token[2:])
        elif token_l in ABBREVIATIONS:
            kept.append(ABBREVIATIONS[token_l])
        elif token[0].islower() and token not in ("of", "and"):
            kept.append(token[0].upper() + token[1:])
        else:
            kept.append(token)

    expanded = PATTERN_OVERRIDES(" ".join(kept))

    for abbr, full in CONTEXTUAL_ABBREVIATIONS:
        if re.search(abbr + "($| )", expanded):
            expanded = expanded.replace(abbr, full)

    if m := re.search(r"([A-Z]) (\d{1,5})$", expanded):
        expanded = expanded[: m.start(1)] + m.group(1) + m.group(2)

    if expanded.endswith("- TBL"):
        expanded = expanded[: -len("- TBL")].strip()

    log.debug("Expanded to: %s", expanded)
    return expanded


def match_building_and_room(s):
    if s.startswith(("Tent - ", "Off Campus")):
        return None

    if m := re.match(r"(.+) Room ([A-Z]?-?\d{1,5}[A-Z]?)( Intl lng| Lounge)?$", s):
        return [m.group(1), m.group(2)]
    if m := re.match(r"(.+) Room( TBA|$)", s):
        return [m.group(1), None]
    if s.endswith(ACCEPTED_BUILDING_POSTFIXES):
        return [s, None]
    if m := re.match(r"(.+) ([A-Z]?-?\d{1,5}[A-Z]?)$", s):
        return [m.group(1), m.group(2)]
    if s in BUILDING_OVERRIDES:
        return [BUILDING_OVERRIDES[s], None]

    return None


def get_raw_building_room(s: str):
    expanded = expand_text(s)
    match = match_building_and_room(expanded)

    if match is None:
        building_room = RawBuildingRoom(alt=expanded)
    else:
        building_match = BUILDING_MATCH_OVERRIDES.get(match[0], match[0])

        building = BUILDINGS_DICT.get(building_match, None)
        if not building and ("Community College" in building_match or "Mount Ida" in building_match):
            building = RawBuilding(name=building_match, address=None)

        if not building and " " not in building_match:
            postfixes = [" House", " Hall", " Laboratory", " Dorm"]

            while len(postfixes) > 0 and not building:
                building = BUILDINGS_DICT.get(building_match + postfixes.pop(), None)

        if not building:
            best = get_close_matches(building_match, BUILDING_NAMES, cutoff=0.80)
            if len(best) == 1:
                building = BUILDINGS_DICT[best[0]]

        if not building:
            for ending in (" House", " Dormitory"):
                if building_match.endswith(ending):
                    if building := BUILDINGS_DICT.get(building_match[: -len(ending)] + " Hall", None):
                        break

        if building:
            building_room = RawBuildingRoom(building, match[1], expanded)
        else:
            building_room = RawBuildingRoom(alt=expanded)

    log.debug("%s\n\t-> %s\n\t-> %s\n\t-> %s", s, expanded, match, building_room)

    return building_room
