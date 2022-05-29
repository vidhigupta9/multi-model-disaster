from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
import operator
import re
import six.moves.html_parser
from dateutil.parser import _timelex, parser
import string
import os
import six
from six.moves import range
import sys
# sys.setdefaultencoding('utf8')


def regex_or(*items):
    return '(?:' + '|'.join(items) + ')'


Contractions = re.compile("(?i)(\w+)(n['’′]t|['’′]ve|['’′]ll|['’′]d|['’′]re|['’′]s|['’′]m)$", re.UNICODE)
Whitespace = re.compile("[\s\u0020\u00a0\u1680\u180e\u202f\u205f\u3000\u2000-\u200a]+", re.UNICODE)

punctChars = r"['\"“”‘’.?!…,:;]"

punctSeq = r"['\"“”‘’]+|[.?!,…]+|[:;]+"  
entity = r"&(?:amp|lt|gt|quot);"


urlStart1 = r"(?:https?://|\bwww\.)"
commonTLDs = r"(?:com|org|edu|gov|net|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|pro|tel|travel|xxx)"
ccTLDs = r"(?:ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|" + \
         r"bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|" + \
         r"er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|" + \
         r"hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|" + \
         r"lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|" + \
         r"nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|" + \
         r"sl|sm|sn|so|sr|ss|st|su|sv|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|" + \
         r"va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|za|zm|zw)"  
urlStart2 = r"\b(?:[A-Za-z\d-])+(?:\.[A-Za-z0-9]+){0,3}\." + regex_or(commonTLDs,
                                                                      ccTLDs) + r"(?:\." + ccTLDs + r")?(?=\W|$)"
urlBody = r"(?:[^\.\s<>][^\s<>]*?)?"
urlExtraCrapBeforeEnd = regex_or(punctChars, entity) + "+?"
urlEnd = r"(?:\.\.+|[<>]|\s|$)"
url = regex_or(urlStart1, urlStart2) + urlBody + "(?=(?:" + urlExtraCrapBeforeEnd + ")?" + urlEnd + ")"

# Numeric
timeLike = r"\d+(?::\d+){1,2}"
num = r"\d+"
numNum = r"\d+\.\d+"
numberWithCommas = r"(?:(?<!\d)\d{1,3},)+?\d{3}" + r"(?=(?:[^,\d]|$))"
numComb = "[\u0024\u058f\u060b\u09f2\u09f3\u09fb\u0af1\u0bf9\u0e3f\u17db\ua838\ufdfc\ufe69\uff04\uffe0\uffe1\uffe5\uffe6\u00a2-\u00a5\u20a0-\u20b9]?\\d+(?:\\.\\d+)+%?"

# Abbreviations
boundaryNotDot = regex_or("$", r"\s", r"[“\"?!,:;]", entity)
aa1 = r"(?:[A-Za-z]\.){2,}(?=" + boundaryNotDot + ")"
aa2 = r"[^A-Za-z](?:[A-Za-z]\.){1,}[A-Za-z](?=" + boundaryNotDot + ")"
standardAbbreviations = r"\b(?:[Mm]r|[Mm]rs|[Mm]s|[Dd]r|[Ss]r|[Jj]r|[Rr]ep|[Ss]en|[Ss]t)\."
arbitraryAbbrev = regex_or(aa1, aa2, standardAbbreviations)
separators = "(?:--+|―|—|~|–|=)"
decorations = "(?:[♫♪]+|[★☆]+|[♥❤♡]+|[\u2639-\u263b]+|[\ue001-\uebbb]+)"
thingsThatSplitWords = r"[^\s\.,?\"]"
embeddedApostrophe = thingsThatSplitWords + r"+['’′]" + thingsThatSplitWords + "*"

normalEyes = "[:=]"  
wink = "[;]"
noseArea = "(?:|-|[^a-zA-Z0-9 ])" 
happyMouths = r"[D\)\]\}]+"
sadMouths = r"[\(\[\{]+"
tongue = "[pPd3]+"
otherMouths = r"(?:[oO]+|[/\\]+|[vV]+|[Ss]+|[|]+)"  

bfLeft = "(♥|0|[oO]|°|[vV]|\\$|[tT]|[xX]|;|\u0ca0|@|ʘ|•|・|◕|\\^|¬|\\*)"
bfCenter = r"(?:[\.]|[_-]+)"
bfRight = r"\2"
s3 = r"(?:--['\"])"
s4 = r"(?:<|&lt;|>|&gt;)[\._-]+(?:<|&lt;|>|&gt;)"
s5 = "(?:[.][_]+[.])"
basicface = "(?:" + bfLeft + bfCenter + bfRight + ")|" + s3 + "|" + s4 + "|" + s5

eeLeft = r"[＼\\ƪԄ\(（<>;ヽ\-=~\*]+"
eeRight = "[\\-=\\);'\u0022<>ʃ）/／ノﾉ丿╯σっµ~\\*]+"
eeSymbol = r"[^A-Za-z0-9\s\(\)\*:=-]"
eastEmote = eeLeft + "(?:" + basicface + "|" + eeSymbol + ")+" + eeRight

oOEmote = r"(?:[oO]" + bfCenter + r"[oO])"

emoticon = regex_or(
    "(?:>|&gt;)?" + regex_or(normalEyes, wink) + regex_or(noseArea, "[Oo]") + regex_or(tongue + r"(?=\W|$|RT|rt|Rt)",
                                                                                       otherMouths + r"(?=\W|$|RT|rt|Rt)",
                                                                                       sadMouths, happyMouths),

    regex_or("(?<=(?: ))", "(?<=(?:^))") + regex_or(sadMouths, happyMouths, otherMouths) + noseArea + regex_or(
        normalEyes, wink) + "(?:<|&lt;)?",eastEmote.replace("2", "1", 1), basicface,oOEmote
)

Hearts = "(?:<+/?3+)+"  
Arrows = regex_or(r"(?:<*[-―—=]*>+|<+[-―—=]*>*)", "[\u2190-\u21ff]+")

Hashtag = "#[a-zA-Z0-9_]+" 
AtMention = "[@＠][a-zA-Z0-9_]+"

Bound = r"(?:\W|^|$)"
Email = regex_or("(?<=(?:\W))", "(?<=(?:^))") + r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}(?=" + Bound + ")"

Protected = re.compile(
    six.text_type(regex_or(
        Hearts,
        url,
        Email,
        timeLike,
        emoticon,
        Arrows,
        entity,
        punctSeq,
        arbitraryAbbrev,
        separators,
        decorations,
        embeddedApostrophe,
    )), re.UNICODE)

edgePunctChars = "'\"“”‘’«»{}\\(\\)\\[\\]\\*&"  
edgePunct = "[" + edgePunctChars + "]"
notEdgePunct = "[a-zA-Z0-9]"  
offEdge = r"(^|$|:|;|\s|\.|,)"  
EdgePunctLeft = re.compile(offEdge + "(" + edgePunct + "+)(" + notEdgePunct + ")", re.UNICODE)
EdgePunctRight = re.compile("(" + notEdgePunct + ")(" + edgePunct + "+)" + offEdge, re.UNICODE)


def splitEdgePunct(text):
    text = EdgePunctLeft.sub(r"\1\2 \3", text)
    text = EdgePunctRight.sub(r"\1 \2\3", text)
    return text


p = parser()
info = p.info


def dateParse(text):
    pat = re.compile("(DATE[ ]*)+", re.UNICODE)
    text = re.sub(pat, "DATE ", text)
    return text


def timetoken(token):
    try:
        float(token)
        return True
    except ValueError:
        pass
    return any(f(token) for f in
               (info.jump, info.weekday, info.month, info.hms, info.ampm, info.pertain, info.utczone, info.tzoffset))


def timesplit(input_string):
    batch = ""
    for token in input_string.split():
        if timetoken(token):
            if info.jump(token):
                continue
            batch = batch + ""
        else:
            batch = batch + " " + token
    return dateParse(batch)



def digitParse(text):
    pat = re.compile("(DIGIT-DIGIT|DIGIT[ ]*)+", re.UNICODE)
    text = re.sub(pat, " ", text)
    return text


def digit(text):
    # print (text)
    text = re.sub(num, "", text)
    text = re.sub(numNum, "", text)
    text = re.sub(numberWithCommas, "", text)
    text = re.sub(numComb, "", text)
    return digitParse(text)


def urlParse(text):
    pat = re.compile(url, re.UNICODE)
    text = re.sub(pat, "", text)
    return text


def simpleTokenize(text):
    try:
        text = text
    except Exception as e:
        print(e)
        pass
    text = text.lower()  
    text = digit(text)
    text = urlParse(text)
    punc = "[#(),$%^&*+={}\[\]:\"|\~`<>/,¦!?½£¶¼©⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞⅟↉¤¿º;-]+"
    text = re.sub(punc, "", text)
    spchar = "[\x98\x9C\x94\x89\x84\x88\x92\x8F]+"
    text = re.sub(spchar, "", text)
    text = re.sub("--&gt;&gt;|--|-|[\.]+", " ", text)
    text = re.sub("\'", " ", text)
    tweet_words = text.split(' ')
    tWords = []
    for word in tweet_words:
        word = word.strip()
        if ((len(word) > 1 and word[0] == '@')):
            continue
        elif (word == "rt" or word == "userid"):
            continue
        elif (len(word) != 1):
            tWords.append(word)
    text = " ".join(tWords)
    text = re.sub(r"(.)\1\1+", r'\1\1', text)
    splitPunctText = splitEdgePunct(text.strip())
    textLength = len(splitPunctText)

    bads = []
    badSpans = []
    for match in Protected.finditer(splitPunctText):
        if (match.start() != match.end()): 
            bads.append([splitPunctText[match.start():match.end()]])
            badSpans.append((match.start(), match.end()))

    indices = [0]
    for (first, second) in badSpans:
        indices.append(first)
        indices.append(second)
    indices.append(textLength)

    splitGoods = []
    for i in range(0, len(indices), 2):
        goodstr = splitPunctText[indices[i]:indices[i + 1]]
        splitstr = goodstr.strip().split(" ")
        splitGoods.append(splitstr)

    zippedStr = []
    for i in range(len(bads)):
        zippedStr = addAllnonempty(zippedStr, splitGoods[i])
        zippedStr = addAllnonempty(zippedStr, bads[i])
    zippedStr = addAllnonempty(zippedStr, splitGoods[len(bads)])
    return zippedStr  


def addAllnonempty(master, smaller):
    for s in smaller:
        strim = s.strip()
        if (len(strim) > 0):
            master.append(strim)
    return master


def squeezeWhitespace(input):
    return Whitespace.sub(" ", input).strip()


def splitToken(token):
    m = Contractions.search(token)
    if m:
        return [m.group(1), m.group(2)]
    return [token]


def file_exist(file_name):
    if os.path.exists(file_name):
        return True
    else:
        return False


def read_stop_words(file_name):
    if (not file_exist(file_name)):
        print("Please check the file for stop words, it is not in provided location " + file_name)
        exit(0)
    stop_words = []
    with open(file_name, 'r') as f:
        for line in f:
            line = line.strip()
            if (line == ""):
                continue
            stop_words.append(line)
    return stop_words;


stop_words_file = "bin/etc/stop_words_english.txt"
stop_words = read_stop_words(stop_words_file)


def tokenize(text):
    text = simpleTokenize(squeezeWhitespace(text));
    w_list = []
    for w in text:
        if w not in stop_words:
            try:
                w_list.append(w)
            except Exception as e:
                pass
    text = " ".join(text)
    return text


def normalizeTextForTagger(text):
    text = text.replace("&amp;", "&")
    text = six.moves.html_parser.HTMLParser().unescape(text)
    return text


def tokenizeRawTweetText(text):
    tokens = tokenize(normalizeTextForTagger(text))
    return tokens
