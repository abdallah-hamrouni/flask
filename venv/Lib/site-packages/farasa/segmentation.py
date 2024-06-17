import operator
import re
import math
from . import fitTemplateClass as ft
from .arabic_utils import utilities
import pickle

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources # Try backported to PY<37 `importlib_resources`.
from . import pickles


def deserializeMap(file_name):
    try:
        with pkg_resources.open_binary(pickles, file_name) as pf:
            return pickle.load(pf)
    except FileNotFoundError:
        raise FileNotFoundError(f"Missing file {file_name}")


hmListMorph = deserializeMap("hmListMorph")
hmListGaz = deserializeMap("hmListGaz")
hmAraLexCom = deserializeMap("hmAraLexCom")
hmBuck = deserializeMap("hmBuck")
hmLocations = deserializeMap("hmLocations")
hmPeople = deserializeMap("hmPeople")
hmStop = deserializeMap("hmStop")
hPrefixes = deserializeMap("hPrefixes")
hSuffixes = deserializeMap("hSuffixes")
hmValidSuffixes = deserializeMap("hmValidSuffixes")
hmValidPrefixes = deserializeMap("hmValidPrefixes")
hmTemplateCount = deserializeMap("hmTemplateCount")
hmValidSuffixesSegmented = deserializeMap("hmValidSuffixesSegmented")
hmValidPrefixesSegmented = deserializeMap("hmValidPrefixesSegmented")
wordCount = deserializeMap("wordCount")
probPrefixes = deserializeMap("probPrefixes")
probSuffixes = deserializeMap("probSuffixes")
probCondPrefixes = deserializeMap("probCondPrefixes")
probCondSuffixes = deserializeMap("probCondSuffixes")
seenTemplates = deserializeMap("seenTemplates")
hmPreviouslySeenTokenizations = deserializeMap("hmPreviouslySeenTokenizations")
hmWordPossibleSplits = deserializeMap("hmWordPossibleSplits")
probPrefixSuffix = deserializeMap("probPrefixSuffix")
probSuffixPrefix = deserializeMap("probSuffixPrefix")
generalVariables = deserializeMap("generalVariables")
hmSeenBefore = deserializeMap("hmSeenBefore")


def segmentLine(arabic_text):
    output = list()
    txt = utilities.removeDiacritics(arabic_text)
    words = utilities.tokenize(txt)
    for word in words:
        if word not in hmSeenBefore:
            solutions = mostLikelyPartition((word), 1)
            topSolution = word
            if len(solutions) > 0:
                topSolution = solutions[0][1]
            topSolution = topSolution.replace(";", "").replace("++", "+")
            if topSolution.startswith("+"):
                topSolution = topSolution[1:]
            if topSolution.endswith("+"):
                topSolution = topSolution[:-1]

            hmSeenBefore[word] = topSolution
            output.append(topSolution.replace("++", "+"))
        else:
            topSolution = hmSeenBefore[word].replace(";", "").replace("++", "+")
            if topSolution.startswith("+"):
                topSolution = topSolution[1:]
            if topSolution.endswith("+"):
                topSolution = topSolution[:-1]
            output.append(topSolution)

    return output


def mostLikelyPartition(word, numberOfSolutions):
    word = word.strip()
    possiblePartitions = getAllPossiblePartitionsOfString(word)
    if word.startswith("\u0644\u0644"):
        possiblePartitions.extend(getAllPossiblePartitionsOfString("\u0644\u0627\u0644" + word[2:]))
    elif word.startswith("\u0648\u0644\u0644"):
        possiblePartitions.extend(getAllPossiblePartitionsOfString("\u0648\u0644\u0627\u0644" + word[3:]))
    elif word.startswith("\u0641\u0644\u0644"):
        possiblePartitions.extend(getAllPossiblePartitionsOfString("\u0641\u0644\u0627\u0644" + word[3:]))

    # score all the different options
    scores = dict()
    if word.replace("+", "") in hmPreviouslySeenTokenizations:
        for p in hmPreviouslySeenTokenizations.get(word.replace("+", "")):
            pp = getProperSegmentation(p.replace(";", ""))
            parts = (" " + pp + " ").split(";")
            score = scorePartition(parts)
            while score in scores:
                score -= 0.00001
            scores[score] = pp
    else:
        for p in possiblePartitions:
            pp = getProperSegmentation(p.replace(";", ""))
            parts = (" " + pp + " ").split(";")
            if len(parts) == 3:
                score = scorePartition(parts)
                while score in scores:
                    score -= 0.00001
                scores[score] = pp

    sorted_scores = sorted(scores.items(), key=operator.itemgetter(0), reverse=True)

    possiblePartitions.clear()
    scores.clear()
    # keep the top 3 segmentations and throw away the rest
    return sorted_scores[:3]


def getAllPossiblePartitionsOfString(s):
    output = list()
    if len(s) > 20:
        output.append(s)
    else:
        s = s.strip()
        if len(s) > 0:
            fullPartition = ','.join(list(s))
            correctFullPartition = getProperSegmentation(re.sub("\\++", '+', fullPartition.replace(",", "+")))
            parts = (" " + correctFullPartition + " ").split(";")

            if correctFullPartition not in output:
                if len(parts[1]) != 1 or len(s) == 1:
                    output.append(correctFullPartition)

            if "," in fullPartition:
                output = getSubPartitions(fullPartition, output)
    return output


def getSubPartitions(s, output):
    if "," in s:
        parts = s.split(",")
        for i, part in enumerate(parts[:-1]):
            ss = ""
            # construct string with 1 units until i
            for j in range(i):
                if j == 0:
                    ss = parts[j]
                else:
                    ss += "," + parts[j]

            # put 2 units
            if i == 0:
                ss = part + parts[i + 1]
            else:
                ss += "," + part + parts[i + 1]

            # put remaining 1 units until end of string
            for k in range(i+2, len(parts)):
                if k == 0:
                    ss = parts[k]
                else:
                    ss += "," + parts[k]

            tempss = ss.replace(",", "+")
            tempss = re.sub("\\++", "+", tempss)
            properSeg = getProperSegmentation(tempss)

            if properSeg not in output:
                output.append(properSeg)
                if "," in ss:
                    output = getSubPartitions(ss, output)
    return output


def getProperSegmentation(some_string):
    if '+' not in some_string:
        return f';{some_string};'
    word = some_string.split('+')
    currentPrefix = ""
    currentSuffix = ""
    iValidPrefix = -1

    while iValidPrefix + 1 < len(word) and word[iValidPrefix + 1] in hPrefixes.keys():
        iValidPrefix += 1

    iValidSuffix = len(word)

    while iValidSuffix > max(iValidPrefix, 0) and (
                    word[iValidSuffix - 1] in hSuffixes.keys() or word[iValidSuffix - 1] == "_"):
        iValidSuffix -= 1

    for i in range(iValidPrefix + 1):
        currentPrefix += word[i] + '+'

    stemPart = ""

    for i in range(iValidPrefix + 1, iValidSuffix):
        stemPart += word[i]

    if iValidSuffix == iValidPrefix:
        iValidSuffix += 1

    for i in range(iValidSuffix, len(word)):
        if iValidPrefix != iValidSuffix:
            currentSuffix += '+' + word[i]

    if currentSuffix.endswith('\u0633+') and not re.match("^[ينأت].*", stemPart):
        currentPrefix = currentPrefix[:-2]
        stemPart = '\u0633' + stemPart

    output = currentPrefix + ';' + stemPart + ';' + currentSuffix
    output = re.sub("^\\+", '', output, 1)
    output = re.sub("\\+$", '', output, 1)
    return output.replace('++', '+')

def scorePartition(parts):
    score = 0
    prefix = parts[0].strip()
    suffix = parts[2].strip()
    stem = parts[1].strip()

    # assemble score
    # magicNumbers = "1:-0.23482376 2:-0.21097635 3:0.25787985 4:0.16191271 5:0.13404779 6:0.79553878 7:0.27828842 8:-0.21669699 9:0.65872103 10:0.63085192 11:-0.10308913 12:0.10140695".split(" +")
    magicNumbers = "1:-0.097825818 2:-0.03893654 3:0.13109569 4:0.18436976 5:0.11448806 6:0.53001714 7:0.21098258 8:-0.17760228 9:0.44223878 10:0.26183113 11:-0.05603376 12:0.055829503 13:-0.17745291 14:0.015865559 15:0.66909122 16:0.16948195 17:0.15397599 18:0.60355717".split()

    magicNo = list()
    for m in magicNumbers:
        magicNo.append(float(m[m.index(':') + 1:]))

    if prefix in probPrefixes:
        score += magicNo[0] * math.log(probPrefixes.get(prefix))
    else:
        score += magicNo[0] * -10

    if suffix in probSuffixes:
        score += magicNo[1] * math.log(probSuffixes.get(suffix))
    else:
        score += magicNo[1] * -10

    trimmedTemp = suffix.replace("+", "").replace(";", "").replace(",", "")
    altStem = ""

    if trimmedTemp.startswith('\u062A') and len(trimmedTemp) > 1:
        altStem = stem + '\u0629'

    stemWordCount = -10

    if stem in wordCount:
        stemWordCount = wordCount.get(stem)
    elif len(altStem) > 1 and altStem in wordCount:  # && wordCount.get(altStem) > stemWordCount)
        stemWordCount = wordCount.get(altStem)

    score += magicNo[2] * stemWordCount

    if prefix in probPrefixSuffix and suffix in probPrefixSuffix.get(prefix):
        score += magicNo[3] * math.log(probPrefixSuffix.get(prefix).get(suffix))
    else:
        score += magicNo[3] * -20

    if suffix in probSuffixPrefix and prefix in probSuffixPrefix.get(suffix):
        score += magicNo[4] * math.log(probSuffixPrefix.get(suffix).get(prefix))
    else:
        score += magicNo[4] * -20

    if ft.fitTemplate(stem) != "Y":
        score += magicNo[5] * math.log(generalVariables.get("hasTemplate"))
    else:
        score += magicNo[5] * math.log(1 - generalVariables.get("hasTemplate"))

    if stem in hmListMorph or (stem.endswith('\u064A') and stem[:-1] + '\u0649' in hmListMorph):
        score += magicNo[6] * math.log(generalVariables.get("inMorphList"))
    else:
        score += magicNo[6] * math.log(1 - generalVariables.get("inMorphList"))

    if stem in hmListGaz or (stem.endswith('\u064A') and stem[:-1] + '\u0649' in hmListGaz):
        score += magicNo[7] * math.log(generalVariables.get("inGazList"))
    else:
        score += magicNo[7] * math.log(1 - generalVariables.get("inGazList"))

    if prefix in probCondPrefixes:
        score += magicNo[8] * math.log(probCondPrefixes.get(prefix))
    else:
        score += magicNo[8] * -20

    if suffix in probCondSuffixes:
        score += magicNo[9] * math.log(probCondSuffixes.get(suffix))
    else:
        score += magicNo[9] * -20

    # get probability with first suffix . for example xT + p would produce xTp
    stemPlusFirstSuffix = stem

    if suffix.find("+", 1) > 0:
        stemPlusFirstSuffix += suffix[1:suffix.find("+", 1)]
    else:
        stemPlusFirstSuffix += suffix

    trimmedTemp = stemPlusFirstSuffix.replace("+", "").replace(";", "").replace(",", "")
    stemWordCount = -10

    if stemPlusFirstSuffix in wordCount:
        stemWordCount = wordCount.get(stemPlusFirstSuffix)
    elif stem.endswith('\u064A') and stem[:-1] + '\u0649' in wordCount:
        stemWordCount = wordCount.get(stem[:-1] + '\u0649')
    elif stemPlusFirstSuffix.endswith('\u062A') and stemPlusFirstSuffix[:-1] + '\u0629' in wordCount:
        stemWordCount = wordCount.get(stemPlusFirstSuffix[:-1] + '\u0629')

    score += magicNo[10] * stemWordCount

    # put template feature
    template = ft.fitTemplate(stem)
    if template in hmTemplateCount:
        score += magicNo[11] * math.log(hmTemplateCount.get(template))
    else:
        score += magicNo[11] * -10

    # difference from average length
    score += magicNo[12] * math.log(abs(len(stem) - generalVariables.get("averageStemLength")))
    trimmedTemp = suffix.replace("+", "").replace(";", "").replace(",", "")
    altStem = ''

    if trimmedTemp.startswith('\u062A') and len(trimmedTemp) > 1:
        altStem = stem + '\u0629'

    if stem in wordCount:
        stemWordCount = wordCount.get(stem)
    elif stem.endswith('\u064A') and stem[:-1] + '\u0649' in wordCount:
        stemWordCount = wordCount.get(stem[:-1] + '\u0649')
    elif len(altStem.strip()) > 0 and altStem in wordCount:
        stemWordCount = wordCount.get(altStem)

    if stem in hmAraLexCom:
        if stem in wordCount:
            score += magicNo[13] * wordCount.get(stem)
        else:
            score += magicNo[13] * -10
    elif stem.endswith('\u064A') and stem[:-1] + '\u0649' in hmAraLexCom:
        if stem[:-1] + '\u0649' in wordCount:
            score += magicNo[13] * wordCount.get(stem[:-1] + '\u0649')
        else:
            score += magicNo[13] * -10
    elif len(altStem.strip()) > 0 and altStem in hmAraLexCom:
        if altStem in wordCount:
            score += magicNo[13] * wordCount.get(altStem)
        else:
            score += magicNo[13] * -10
    else:
        score += magicNo[13] * -20

    if stem in hmBuck:
        score += magicNo[14]
    elif stem.endswith('\u064A') and stem[:-1] + '\u0649' in hmBuck:
        score += magicNo[14]
    else:
        score += -1 * magicNo[14]

    if stem in hmLocations:
        score += magicNo[15]
    else:
        score += -1 * magicNo[15]

    if stem in hmPeople:
        score += magicNo[16]
    else:
        score += -1 * magicNo[16]

    if stem in hmStop:
        score += magicNo[17]
    elif stem.endswith('\u064A') and stem[:-1] + '\u0649' in hmStop:
        score += magicNo[17]
    else:
        score += -1 * magicNo[17]

    return score


if __name__ != "__main__":
    pass
