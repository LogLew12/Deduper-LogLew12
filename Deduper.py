import argparse
import re

def get_args():
    parser = argparse.ArgumentParser(
        description="Removes PCR duplicates from a sorted SAM file"
    )
    parser.add_argument("-u", "--umi", help="file containing all known umis (one on each line)", required=True)
    parser.add_argument("-f", "--file", help="input file name", required=True)
    parser.add_argument("-p", "--paired", nargs ='?', const='paired', default='single', help="output file name")
    return parser.parse_args()

args = get_args()

#checking if user flagged their data as paired end
if args.paired == 'paired':
    raise Exception("This program does not yet support paired-end data")

#creating a list of all given umis
umis = []
with open(args.umi) as fh_umi:
    for line in fh_umi:
        line = line.strip()
        umis.append(line)

#opening and renaming an output file
filename = args.file[0:-4]
fh_out = open(f"{filename}_deduped.sam", "w")

def fix_pos(pos, cigar, rev_comp_status):
    '''Given a read starting position (int), a CIGAR string (str), and whether or not a read
    maps to the reverse strand of the reference (bool), returns a corrected start position for that
    reads alignment.'''
    #regex to create two list, one contains cigar string numbers, the other has its letters
    cigar_nums = re.findall("\d+", cigar)
    cigar_lets = re.findall("[A-Z]", cigar)

    #if the read is from the plus strand
    if rev_comp_status == False:
        #if theres soft-clipping at the start
        if cigar_lets[0] == "S":
            pos = pos - int(cigar_nums[0])
            return pos
        #if theres no soft-clipping
        else:
            return pos
    
    #if the read is from the minus strand
    else:
        #We don't want to count softclipping at the start of the string
        if cigar_lets[0] == "S":
            for i, let in enumerate(cigar_lets[1:]):
                #We don't want to count insertions here, but we want everyting else
                if let == "I":
                    continue
                else:
                    pos += int(cigar_nums[i + 1])
            return pos
        else:
            for i, let in enumerate(cigar_lets):
                if let == "I":
                    continue
                else:
                    pos += int(cigar_nums[i])
            return pos

wrong_umi_counter = 0
Deduped_lines = {}
with open(args.file) as fh:
    for line in fh:
        line = line.strip()

        #writes header lines to output file
        if line.startswith("@"):
            fh_out.write(line + "\n")
            continue
        
        #storing the previous chromosome. Try/except to handle the the first line, before chrom is defined
        try:
            prev_chrom = chrom
        except:
            prev_chrom = "placeholder"

        sam_fields = line.split("\t")
        #grabs umi from qname
        umi = sam_fields[0].split(":")[-1]
        #checks if this umi is in given list
        if umi not in umis:
            wrong_umi_counter += 1
            continue
        
        #grabbing variables needed for identifing pcr dupes
        flag = int(sam_fields[1])
        rev_comp_status = ((flag & 16) == 16)
        pos = int(sam_fields[3])
        cigar = sam_fields[5]
        chrom = sam_fields[2]


        pos = fix_pos(pos, cigar, rev_comp_status)
        read_info = (pos, umi, rev_comp_status)
        
        #if chromosome changes, write all lines in dict to output and empty the dict
        if chrom != prev_chrom:
            for sam_line in Deduped_lines.values():
                fh_out.write(sam_line + "\n")
            Deduped_lines = {}
        
        #if unique read info is not already in the dict, add it. Otherwise go to the next line
        if read_info not in Deduped_lines:
            Deduped_lines[read_info] = line

#writing the lines from the last chromosome to the output file
for sam_line in Deduped_lines.values():
    fh_out.write(sam_line + "\n")

print(wrong_umi_counter)
fh_out.close()