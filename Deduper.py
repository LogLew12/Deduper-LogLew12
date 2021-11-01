import argparse
import re

def get_args():
    parser = argparse.ArgumentParser(
        description="Plots median quality scores for a given fastq file"
    )
    parser.add_argument("-u", "--umi", help="file containing all known umis (one on each line", required=True)
    parser.add_argument("-f", "--file", help="input file name", required=True)
    parser.add_argument("-o", "--output", help="output file name", required=True)
    return parser.parse_args()

args = get_args()

#creating a list of all given umis
umis = []
with open(args.umi) as fh_umi:
    for line in fh_umi:
        line = line.strip()
        umis.append(line)

#opening an output file
fh_out = open(args.output, "w")

def fix_pos(pos, cigar, rev_comp_status):
    '''DOC STRING'''
    #regex to create two list, one contains cigar string numbers, the other has letters
    cigar_nums = re.findall("\d+", cigar)
    cigar_lets = re.findall("[A-Z]", cigar)

    #if the read is from the plus strand
    if rev_comp_status == False:
        #if theres soft-clipping
        if cigar_lets[0] == "S":
            pos = pos - int(cigar_nums)
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
                    pos += int(cigar_nums)
            return pos
        else:
            for i, let in enumerate(cigar_lets):
                if let == "I":
                    continue
                else:
                    pos += int(cigar_nums)
            return pos


Deduped_lines = {}
with open(args.file) as fh:
    for line in fh:
        line = line.strip()
        prev_chrom = chrom

        #writes header lines to output file
        if line.startswith("@"):
            fh_out.write(line + "\n")
            continue

        sam_fields = line.split("\t")
        #grabs umi from qname
        umi = sam_fields[0].split(":")[-1]
        #checks if this umi is in given list
        if umi not in umis:
            continue
        
        #grabbing variables needed for identifing pcr dupes
        int flag = int(sam_fields[1])
        bool rev_comp_status = ((flag & 16) == 16)
        int pos = int(sam_fields[3])
        str cigar = sam_fields[5]
        str chrom = sam_fields[2]

        pos = fix_pos(pos, cigar, rev_comp_status)
        read_info(pos, umi, rev_comp_status)
        if chrom != prev_chrom:
            for sam_line in Deduped_lines.values():
                fh_out.write(sam_line + "\n")
            Deduped_lines = {}
        if read_info not in Deduped_lines:
            Deduped_lines[read_info] = line

for sam_line in Deduped_lines.values():
    fh_out.write(sam_line + "\n")

        
fh_out.close()

