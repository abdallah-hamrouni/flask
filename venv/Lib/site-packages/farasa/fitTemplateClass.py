# -*- coding:utf-8 -*-
from .arabic_utils import utilities
import re
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources
from . import pickles


hmRoot = dict()
hmTemplate = dict()
Templates = dict()  # new HashMap<Integer, ArrayList<String>>();
affixes = list()
hmSeenBefore = dict()

with pkg_resources.open_text(pickles, 'roots.txt', encoding='utf-8') as rootFile:
    for line in rootFile:
        parts = line.strip().split()
        if len(parts) == 2:
            hmRoot[parts[0]] = float(parts[1])

with pkg_resources.open_text(pickles, 'template-count.txt', encoding='utf-8') as tcFile:
    for line in tcFile:
        parts = line.strip().split()
        if len(parts) == 2:
            length = len(parts[0])
            if length not in Templates:
                Templates[length] = list()
            Templates[length].append(parts[0])
            if parts[0] not in hmTemplate:
                hmTemplate[parts[0]] = float(parts[1])

for fix in utilities.prefixes:
    affixes.append(fix)

for fix in utilities.suffixes:
    affixes.append(fix)


def fitTemplate(line: str) -> str:
    if line in hmSeenBefore:
        hmSeenBefore.get(line)
    tmp = fitStemTemplate(utilities.utf82buck(line))

    # ends with ta marbouta or alef maqsoura
    if 'Y' in tmp and line.endswith(('\u0629', '\u064a')):
        tmp = fitStemTemplate(utilities.utf82buck(line[:-1]))

    if 'Y' in tmp and line.endswith('\u064a\u0629'):
        tmp = fitStemTemplate(utilities.utf82buck(line[:-2]))

    if 'Y' in tmp and line.endswith("\u0649"):
        tmp = fitStemTemplate(utilities.utf82buck(line[:-1] + "\u064a"))

    # // contains any form of alef
    if 'Y' in tmp and re.search('[\u0623\u0622\u0625]', line):
        tmp = fitStemTemplate(utilities.utf82buck(re.sub('[\u0623\u0622\u0625]', '\u0627', line)))

    if 'Y' in tmp and len(line) > 1:
        tmp = fitStemTemplate(utilities.utf82buck(line + line[-1:]))

    if 'Y' in tmp and line.startswith("\u0627\u062A"):
        tmp = fitStemTemplate(utilities.utf82buck(line[:1] + "\u0648" + line[1:]))

    if 'Y' in tmp and len(line) >= 5 and re.match('[\u0637\u062F]$', line[2:3]):
        potential = fitStemTemplate(utilities.utf82buck(line[:2] + "\u062A" + line[3:]))
        if len(potential) > 3 and potential[2:3] == "t":
            tmp = potential

    if 'Y' in tmp and "\u0622" in line:
        tmp = fitStemTemplate(utilities.utf82buck(line.replace("\u0622", "\u0623\u0627")))

    if 'Y' in tmp and re.search('[\u0624\u0626]', line):
        tmp = fitStemTemplate(utilities.utf82buck(line.replace("\u0626", "\u0621").replace("\u0624", "\u0621")))
    hmSeenBefore[line] = tmp
    return tmp


def fitStemTemplate(stem: str) -> str:
    template = list()
    length = len(stem)

    if length not in Templates:
        template.append("Y")
        return "Y"
    elif length == 2:
        if utilities.buck2morph(stem + stem[1:]) in hmRoot:
            template.append("fE")
            return "fE"
    else:
        t = Templates[length]
        for s in t:
            root = ""
            lastF = -1
            lastL = -1
            broken = False
            for i, ch in enumerate(s):
                if broken == False:
                    if ch == "f":
                        root += ch
                    elif ch == "E":
                        # check if repeated letter in the root
                        if lastF == -1:  # letter not repeated
                            root += stem[i:i + 1]
                            lastF = i
                        else:  # letter repeated
                            if stem[i:i + 1] != stem[lastF:lastF+1]:
                                # stem template is broken
                                broken = True
                    elif ch == "l":
                        # check if repeated letter in the root
                        if lastL == -1:  # letter not repeated
                            root += stem[i:i + 1]
                            lastL = i
                        else:
                            if stem[i:i + 1] != stem[lastL:lastL+1]:
                                # stem template is broken
                                broken = True
                    elif ch == "C":
                        root += stem[i:i + 1]
                    else:
                        if stem[i:i + 1] != s[i:i + 1]:
                            # template is broken
                            broken = True
                else:
                    break

        root = utilities.buck2morph(root)
        altRoot = list()

        if not broken and root not in hmRoot:
            for j, ch in enumerate(root):
                if ch == "y" or ch == "A" or ch == "w":
                    head = root[:j]
                    tail = root[j + 1:]
                    if head + "w" + tail in hmRoot:
                        altRoot.append(head + "w" + tail)
                    if head + "y" + tail in hmRoot:
                        altRoot.append(head + "y" + tail)
                    if head + "A" + tail in hmRoot:
                        altRoot.append(head + "A" + tail)

        if not broken and root in hmRoot:
            template.append(s + "/" + root)

        for ss in altRoot:
            template.append(s + "/" + ss)

    if len(template) == 0:
        template.append("Y")
        return "Y"

    templateWithC = list()
    templateWithoutC = list()

    for ss in template:
        if "C" in ss:
            templateWithC.append(ss)
        else:
            templateWithoutC.append(ss)

    if len(templateWithoutC) == 0:
        return getBestTemplate(template)
    else:
        return getBestTemplate(templateWithoutC)


def getBestTemplate(template):
    bestScore = 0
    bestTemplate = ""

    for s in template:
        parts = s.split("/")
        if len(parts) == 2:
            score = hmRoot[parts[1]] * hmTemplate[parts[0]]
            if bestScore < score:
                bestScore = score;
                bestTemplate = parts[0]

    return bestTemplate

