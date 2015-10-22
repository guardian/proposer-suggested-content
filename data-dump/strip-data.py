import re, argparse, string

parser = argparse.ArgumentParser(description="Clean plaintext for training by word2vec")
parser.add_argument('textfile', metavar='text-file', type=str, help="The file to strip")


def prep_string(s):
    # remove twitter handles and usernames altogether as well as hashtags
    # because no one cares about those
    no_handles = re.sub(re.compile('(\s+|^)@\S+'), ' ', s)
    no_twitter = re.sub(re.compile('(?:#[\w-]+\s*)+$'), ' ', no_handles)

    # get rid of dashes that occur outside a {word}-{word} format
    tmp = re.sub(re.compile('( |^)-+|-+( |$)'), ' ', no_twitter)

    # singularise apostrophe jobs
    next = tmp.replace("'s", "")

    # strip all remaining punctuation apart from hypens - replace with a space to avoid
    # badly punctuated words issues e.g. string,fun fun.string - punctuation should always
    # be followed with a space
    ret = re.sub('[%s]' % re.escape(string.punctuation.replace('-', '')), ' ', next)

    # lowercase everything and return
    return ret.lower()


if __name__ == "__main__":
    args = vars(parser.parse_args())

    input_file = args['textfile']
    out_file = input_file + "-stripped"


    print("Stripping data from: " + str(input_file))
    print("Writing stripped data to: " + str(out_file))

    segment = 10000000    # the amount of lines to write back at a time
    lines = []
    with open(input_file, "r") as r, open(out_file, "w") as w:
        for line in r:
            # do the processing and write the file
            lines.append(prep_string(line))
            if len(lines) == segment:
                w.writelines(lines)
                lines = []
        w.writelines(lines)
