import sys
from re import sub
import codecs
import string

regexes = [
(r"ö(?!(([^']*'){2})*([^']*'))",r"o"), #match ö not followed by odd number of ' (does not handle escaped ')
(r"å(?!(([^']*'){2})*([^']*'))",r"a"),
(r"ä(?!(([^']*'){2})*([^']*'))",r"a"),
(r'\[from\]', r'"from"')
]

def convert(s):
    t = s.strip()

    if not t.startswith('(') and not t.startswith('INSERT') and not t.startswith('VALUES'):
        return None

    for (rx, rep) in regexes:
        t = sub(rx, rep, t)

    t = t.replace('\r\n', '\n')
    t = t.replace('\r', '\n')
    return t

def main():
    if len(sys.argv) < 2:
        print("Specify file on command line.")
        exit()

    filename = sys.argv[1]

    f_in = codecs.open(filename, 'r',encoding='utf-8')#open(filename, 'r')
    f_out = codecs.open('psql_{}'.format(filename),'w', encoding='utf-8') #open('psql_{}'.format(filename),'w')

    f_out.write('BEGIN;\n')
    for line in f_in:
        converted = convert(line)
        if not converted is None:
            f_out.write(converted)
            f_out.write('\n')
    f_out.write('COMMIT;\n')


if __name__ == '__main__':
    main()