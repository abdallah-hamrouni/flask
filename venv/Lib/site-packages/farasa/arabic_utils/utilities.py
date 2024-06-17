# -*- coding:utf-8 -*-
import re
import codecs

# ALL Arabic letters \U0621-\U063A\U0641-\U064A
AllArabicLetters = "\u0621\u0622\u0623\u0624\u0625\u0626\u0627\u0628\u0629\u062A\u062B\u062C\u062D\u062E\u062F" \
                   + "\u0630\u0631\u0632\u0633\u0634\u0635\u0636\u0637\u0638\u0639\u063A\u0641\u0642\u0643\u0644\u0645\u0646\u0647\u0648\u0649\u064A"

AllArabicDiacritics = "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652";

# ALL Hindi digits \U0660-\U0669
AllHindiDigits = "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669"

# ALL Arabic letters and Hindi digits \U0621-\U063A\U0641-\U064A\U0660-\U0669
AllArabicLettersAndHindiDigits = "\u0621\u0622\u0623\u0624\u0625\u0626\u0627\u0628\u0629\u062A\u062B\u062C\u062D\u062E\u062F" \
                                 + "\u0630\u0631\u0632\u0633\u0634\u0635\u0636\u0637\u0638\u0639\u063A\u0641\u0642\u0643\u0644\u0645\u0646\u0647\u0648\u0649\u064A\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669"

AllDigits = "0123456789"
ALLDelimiters = "\u0020\u0000-\u002F\u003A-\u0040\u007B-\u00BB\u005B-\u005D\u005F-\u0060\\^\u0600-\u060C\u06D4-\u06ED\ufeff"

ArabicStopWords = list()

ALEF = '\u0627'
ALEF_MADDA = '\u0622'
ALEF_HAMZA_ABOVE = '\u0623'
ALEF_HAMZA_BELOW = '\u0625'

HAMZA = '\u0621'
HAMZA_ON_NABRA = '\u0624'
HAMZA_ON_WAW = '\u0626'

YEH = '\u064A'
DOTLESS_YEH = '\u0649'

TEH_MARBUTA = '\u0629'
HEH = '\u0647'

ar = "\u0627\u0625\u0622\u0623\u0621\u0628\u062a\u062b\u062c\u062d\u062e\u062f\u0630\u0631\u0632\u0633\u0634\u0635\u0636\u0637\u0638\u0639\u063a\u0641\u0642\u0643\u0644\u0645\u0646\u0647\u0648\u064a\u0649\u0629\u0624\u0626\u064e\u064b\u064f\u064c\u0650\u064d\u0652\u0651"
buck = "A<|>'btvjHxd*rzs$SDTZEgfqklmnhwyYp&}aFuNiKo~"
b2a_translation_table = str.maketrans(buck, ar)
a2b_translation_table = str.maketrans(ar, buck)

emailRegex = re.compile("[a-zA-Z0-9\\-\\._]+@[a-zA-Z0-9\\-\\._]+$")
pAllDiacritics = re.compile("[\u0640\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670]")
pAllNonCharacters = re.compile("[\u0020\u2000-\u200F\u2028-\u202F\u205F-\u206F\uFEFF]+")
pAllDelimiters = re.compile("[" + ALLDelimiters + "]+")

# "ال", "و", "ف", "ب", "ك", "ل", "لل"
prefixes = ("\u0627\u0644", "\u0648", "\u0641", "\u0628", "\u0643", "\u0644", "\u0644\u0644", "س")

# "ه", "ها", "ك", "ي", "هما", "كما", "نا", "كم", "هم", "هن", "كن", "ا", "ان", "ين", "ون", "وا", "ات", "ت", "ن", "ة"
suffixes = ("\u0647", "\u0647\u0627", "\u0643", "\u064a", "\u0647\u0645\u0627", "\u0643\u0645\u0627", "\u0646\u0627",
            "\u0643\u0645", "\u0647\u0645", "\u0647\u0646", "\u0643\u0646", "\u0627", "\u0627\u0646", "\u064a\u0646",
            "\u0648\u0646", "\u0648\u0627", "\u0627\u062a", "\u062a", "\u0646", "\u0629", "\u062A\u0645")

# ArabicStopWords = ("و", "ما", "هي", "هو", "هم", "هما", "هن", "هذا", "هذه", "هذان", "هؤلاء", "هل", "في", "هنا", "هناك",
# "مع", "من", "علي", "كيف", "كان")
ArabicStopWords = (
    "\u0648", "\u0645\u0627", "\u0647\u064A", "\u0647\u0648", "\u0647\u0645", "\u0647\u0645\u0627", "\u0647\u0646",
    "\u0647\u0630\u0627", "\u0647\u0630\u0647", "\u0647\u0630\u0627\u0646", "\u0647\u0624\u0644\u0627\u0621",
    "\u0647\u0644", "\u0641\u064A", "\u0647\u0646\u0627", "\u0647\u0646\u0627\u0643", "\u0645\u0639", "\u0645\u0646",
    "\u0639\u0644\u064A", "\u0643\u064A\u0641", "\u0643\u0627\u0646")


def buck2morph(kdinput):
    # buck = "$Y\'|&}*<>&}"
    # morph = "PyAAAAOAAAA"
    # kdinput = kdinput.replace(buck, morph);
    kdinput = kdinput.replace('$', 'P').replace('Y', 'y').replace('\'', 'A').replace('|', 'A').replace('&',
                                                                                                       'A').replace('}',
                                                                                                                    'A').replace(
        '*', 'O');
    kdinput = kdinput.replace("<", "A").replace(">", "A").replace("&", "A").replace("'", "A").replace("}", "A");
    return kdinput;


def utf82buck(kdinput):
    return kdinput.translate(a2b_translation_table)


def utf82buckWithoutDiacritics(kdinput):
    kdinput = kdinput.replace("\u0627", "A").replace("\u0625", "<").replace("\u0622", "|").replace("\u0623",
                                                                                                   ">").replace(
        "\u0621", "'")
    kdinput = kdinput.replace("\u0628", "b").replace("\u062a", "t").replace("\u062b", "v").replace("\u062c",
                                                                                                   "j").replace(
        "\u062d", "H")
    kdinput = kdinput.replace("\u062e", "x").replace("\u062f", "d").replace("\u0630", "*").replace("\u0631",
                                                                                                   "r").replace(
        "\u0632", "z")
    kdinput = kdinput.replace("\u0633", "s").replace("\u0634", "$").replace("\u0635", "S").replace("\u0636",
                                                                                                   "D").replace(
        "\u0637", "T")
    kdinput = kdinput.replace("\u0638", "Z").replace("\u0639", "E").replace("\u063a", "g").replace("\u0641",
                                                                                                   "f").replace(
        "\u0642", "q")
    kdinput = kdinput.replace("\u0643", "k").replace("\u0644", "l").replace("\u0645", "m").replace("\u0646",
                                                                                                   "n").replace(
        "\u0647", "h")
    kdinput = kdinput.replace("\u0648", "w").replace("\u064a", "y").replace("\u0649", "Y").replace("\u0629",
                                                                                                   "p").replace(
        "\u0624", "&")
    kdinput = kdinput.replace("\u0626", "}")
    return kdinput


def buck2utf8(kdinput):
    return kdinput.translate(b2a_translation_table)


def buck2utf8WithoutDiacritics(kdinput):
    kdinput = kdinput.replace("A", "\u0627").replace("<", "\u0625").replace("|", "\u0622").replace(">",
                                                                                                   "\u0623").replace(
        "'", "\u0621");
    kdinput = kdinput.replace("b", "\u0628").replace("t", "\u062a").replace("v", "\u062b").replace("j",
                                                                                                   "\u062c").replace(
        "H", "\u062d");
    kdinput = kdinput.replace("x", "\u062e").replace("d", "\u062f").replace("*", "\u0630").replace("r",
                                                                                                   "\u0631").replace(
        "z", "\u0632");
    kdinput = kdinput.replace("s", "\u0633").replace("$", "\u0634").replace("S", "\u0635").replace("D",
                                                                                                   "\u0636").replace(
        "T", "\u0637");
    kdinput = kdinput.replace("Z", "\u0638").replace("E", "\u0639").replace("g", "\u063a").replace("f",
                                                                                                   "\u0641").replace(
        "q", "\u0642");
    kdinput = kdinput.replace("k", "\u0643").replace("l", "\u0644").replace("m", "\u0645").replace("n",
                                                                                                   "\u0646").replace(
        "h", "\u0647");
    kdinput = kdinput.replace("w", "\u0648").replace("y", "\u064a").replace("Y", "\u0649").replace("p",
                                                                                                   "\u0629").replace(
        "&", "\u0624");
    kdinput = kdinput.replace("}", "\u0626")
    return kdinput


def tokenizeText(kdinput):
    charInput = list(kdinput)
    kdinput = ""
    for i, ci in enumerate(charInput):
        c = ord(ci)
        if c <= 32 or c == 127 or 194128 <= c <= 194160:
            kdinput += " "
        else:
            kdinput += ci

    zeroWidth_pattern = re.compile("[\u200B\ufeff]+")
    kdinput = zeroWidth_pattern.sub(" ", kdinput)
    kdinput = kdinput.replace('\u0000\u0000\u0000\u0000', '')

    output = list()
    word_split_pattern = re.compile("[\\\u061f \t\n\r,\\-<>\"\\?\\:;\\&]+")
    words = word_split_pattern.split(kdinput)
    # p = re.compile("[a-zA-Z0-9\\-\\._]+@[a-zA-Z0-9\\-\\._]+$")
    for i, word in enumerate(words[:]):
        if word.startswith(("#", "@", ";", "http://")) or re.match("[a-zA-Z0-9\\-\\._]+@[a-zA-Z0-9\\-\\._]+$", word):
            if word.endswith((":", "\'")):
                word = word[:-1]

            output.append(normalize(word.strip()))
        else:
            tmp = pAllDelimiters.split(word)
            for j, word_part in enumerate(tmp[:]):
                tmp[j] = word_part.lstrip("\'").rstrip(":\"'").strip()
                if tmp[j]:
                    output.append(normalize(tmp[j]))

    return output


def tokenizeWithoutProcessing(s):
    output = list()
    s = removeNonCharacters(s)
    s = re.sub("[\t\n\r]", " ", s)

    words = s.split()

    for i, word in enumerate(words):
        if word.startswith(("#", "@", ";", ":", "http://")) or emailRegex.match(word):
            output.append(word)
        else:
            for ss in charBasedTonkenizer(word).split():
                if len(ss.strip()) > 0:
                    if ss.startswith("\u0644\u0644"):
                        output.append("\u0644\u0627\u0644" + ss[2:])
                    else:
                        output.append(ss)

    return output


def removeNonCharacters(s):
    return pAllNonCharacters.sub(' ', s)


def removeDiacritics(s):
    return pAllDiacritics.sub('', s)


def charBasedTonkenizer(s):
    sFinal = ""
    for i, ch in enumerate(s):
        if pAllDelimiters.match(s[i:i + 1]) and s[i:i + 1] != "." and s[i:i + 1] != "," and s[i:i + 1] != "." and s[
                                                                                                                  i:i + 1] != "%":
            sFinal += " " + s[i: i + 1] + " "
        elif s[i: i + 1] == "%":
            if i > 0 and s[i:i + 1] in AllDigits:
                sFinal += s[i:i + 1] + " "
            else:
                sFinal += " " + s[i:i + 1] + " "
        elif s[i:i + 1] == "." or s[i:i + 1] == "," or s[i:i + 1] == ".":
            if 0 < i < len(s) - 1 and s[i - 1: i] in AllDigits and s[i + 1: i + 2] in AllDigits:
                sFinal += s[i: i + 1]
            elif i > 0 and s[i: i + 1] == "." and s[i - 1: i] == ".":
                sFinal += s[i: i + 1]
            elif i == 0:
                sFinal += s[i: i + 1] + " "
            elif i == len(s) - 1:
                sFinal += " " + s[i: i + 1]
            elif s[i - 1:i] in AllDigits and s[i + 1:i + 2] in AllDigits:
                sFinal += s[i: i + 1]
            else:
                sFinal += " " + s[i: i + 1] + " "
        elif s[
             i:i + 1] not in AllArabicLettersAndHindiDigits + "\u0640\u064b\u064c\u064d\u064e\u064f\u0650\u0651\u0652\u0670" + "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ÀÁÂÃÄÅÆÇÈÉËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ":
            sFinal += " " + s[i:i+1] + " "
        else:
            if (i == 0):
                sFinal += s[i: i + 1]
            else:
                if (s[i:i + 1] in AllDigits and s[i - 1: i] in (AllArabicLetters + AllArabicDiacritics)) or (
                                s[i - 1:i] in AllDigits and s[i:i + 1] in (AllArabicLetters + AllArabicDiacritics)):
                    sFinal += " " + s[i: i + 1]
                else:
                    sFinal += s[i: i + 1]

    return sFinal.strip()


def normalize(s):
    if s.startswith("\u0644\u0644"):
        s = "\u0644\u0627\u0644" + s[2:]

    elif s.startswith("\u0648\u0644\u0644"):
        s = "\u0648\u0644\u0627\u0644" + s[3:]

    s = pAllDiacritics.sub('', s)

    return s


def normalizeFull(s):
    if s.startswith("\u0644\u0644"):
        s = "\u0644\u0627\u0644" + s[2:]

    elif s.startswith("\u0648\u0644\u0644"):
        s = "\u0648\u0644\u0627\u0644" + s[3:]

        s = s.replace(ALEF_MADDA, ALEF).replace(ALEF_HAMZA_ABOVE, ALEF).replace(ALEF_HAMZA_BELOW, ALEF)
        s = s.replace(DOTLESS_YEH, YEH)
        s = s.replace(HAMZA_ON_NABRA, HAMZA).replace(HAMZA_ON_WAW, HAMZA)
        s = s.replace(TEH_MARBUTA, HEH)
        s = s.replace("ٱ", "ا")

        s = pAllDiacritics.sub('', s)

    return s


def tokenize(text):
    s = removeNonCharacters(text)
    s = removeDiacritics(s)

    tnr_pattern = re.compile('[\t\n\r]')
    s = tnr_pattern.sub(' ', s)
    output = list()
    words = s.split()

    for i, word in enumerate(words):
        if word.startswith(("#", "@", ":", ";", "http://", "https://")) or emailRegex.match(word):
            output.append(word)
        else:
            for ss in charBasedTonkenizer(word).split():
                if len(ss.strip()) > 0:
                    if ss.startswith("\u0644\u0644"):
                        output.append("\u0644\u0627\u0644" + ss[2:])
                    else:
                        if len(ss.strip()) > 0:
                            output.append(ss)
    return output


def standardizeDiacritics(word):
    diacrtics = "[\u064e\u064b\u064f\u064c\u0650\u064d\u0652\u0651]"
    sokun = "\u0652"
    fatha = "\u064e"

    word = re.sub("^[\u064e\u064b\u064f\u064c\u0650\u064d\u0652\u0651]+", "", word)
    word = word.replace("\u064E\u0627", "\u0627").replace("\u064F\u0648", "\u0648").replace("\u0650\u064A",
                                                                                            "\u064A").replace(
        "\u0622\u064E", "\u0622")

    pos = word.find("\u0648")
    while (0 < pos < len(word) - 1):
        if not re.match(diacrtics, word[pos - 1:pos]) and word[pos + 1:pos + 2] == "\u0652":
            word = word[:pos + 1] + word[pos + 2:]
        pos = word.find("\u0648", pos + 1)

    pos = word.find("\u064A")
    while (0 < pos < len(word) - 1):
        if not re.match(diacrtics, word[pos - 1:pos]) and word[pos + 1:pos + 2] == "\u0652":
            word = word[:pos + 1] + word[pos + 2:]
        pos = word.find("\u064A", pos + 1)

    pos = word.find("\u0627")
    while (0 < pos < len(word) - 1):
        if not re.match(diacrtics, word[pos - 1:pos]) and (
                        word[pos + 1:pos + 2] == "\u0652" or word[pos + 1:pos + 2] == fatha):
            word = word[:pos + 1] + word[pos + 2:]
        pos = word.find("\u0627", pos + 1)

    if word.startswith("\u0627\u0644\u0652"):
        word = "\u0627\u0644" + word[3:]

    return word


def transferDiacriticsFromWordToSegmentedVersion(diacritizedWord, stemmedWord):
    # startsWithLamLam = False
    # startsWithWaLamLam = False
    # startsWithFaLamLam = False

    if stemmedWord.startswith("\u0644+\u0627\u0644") and removeDiacritics(diacritizedWord).startswith(
            "\u0644\u0644") or stemmedWord.startswith("\u0648+\u0644+\u0627\u0644") and removeDiacritics(
        diacritizedWord).startswith("\u0648\u0644\u0644") or stemmedWord.startswith(
        "\u0641+\u0644+\u0627\u0644") and removeDiacritics(diacritizedWord).startswith("\u0641\u0644\u0644"):
        posFirstLam = diacritizedWord.find("\u0644", 0)
        posSecondLam = diacritizedWord.find("\u0644", posFirstLam + 1)
        diacritizedWord = diacritizedWord[0:posSecondLam] + "\u0627" + diacritizedWord[posSecondLam:]

    output = ""
    stemmedWord = stemmedWord.replace(" ", "")
    stemmedWord = re.sub("\\+$", "", stemmedWord, 1)

    if diacritizedWord == stemmedWord or '+' not in stemmedWord:
        return diacritizedWord

    pos = 0
    for ch in stemmedWord:
        if ch == '+' or ch == ';':
            output += ch
        else:
            loc = diacritizedWord.find(ch, pos)
            if loc >= 0:
                diacritics = diacritizedWord[pos: loc]
                output += diacritics + ch
                # add trailing diacritics
                loc += 1
                while loc < len(diacritizedWord) and re.match("[" + buck2utf8("aiouNKF~") + "]",
                                                              diacritizedWord[loc:loc + 1]):
                    output += diacritizedWord[loc:loc + 1]
                    loc += 1
                pos = loc

            else:
                pass

    return output


def getDiacritizedStem(stemmed, diacritized):
    output = str()
    parts = (" " + stemmed + " ").split(';')
    suffixes = parts[2].strip()
    stem = parts[1].strip()

    i = len(diacritized)
    while i>0 and removeDiacritics(diacritized[i:len(diacritized)]) != suffixes:
        i -= 1

    head = diacritized[0:i]
    tail = diacritized[i:]

    i = len(head)

    while i>0 and removeDiacritics(head[i:len(head)]) != stem:
        i -= 1

    diacritizedStem = head[i:]
    return diacritizedStem
