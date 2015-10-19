import re, argparse

parser = argparse.ArgumentParser(description="Clean plaintext for training by word2vec")
parser.add_argument('textfile', metavar='text-file', type=str, help="The file to strip")


def prep_string(s):
#    tmp = re.sub(ur"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " " , s)
    tmp = s
    tmp.replace("'s", "")
    tmp.replace("\"", "")
    tmp.replace(".", " ")
    tmp = re.sub(ur"[^\w\d\-\s]+",'',tmp)
    return tmp

if __name__ == "__main__":
    args = vars(parser.parse_args())

    input_file = args['text_file']
    out_file = input_file + "-stripped"


    print("Stripping data from: " + str(input_file))
    print("Writing stripped data to: " + str(out_file))

    segment = 1000000     # the amount of lines to write back at a time
    lines = []
    with open(input_file, "r") as r, open(out_file, "w") as w:
        for line in r:
            # do the processing and write the file
            if len(lines) == segment:
                w.writelines(lines)
                lines = []
        w.writelines(lines)
