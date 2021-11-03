import re
def fix_pos(pos, cigar, rev_comp_status):
    '''Given a read starting position (int), a CIGAR string (str), and whether or not a read
    maps to the reverse strand of the reference (bool), returns a corrected start position for that
    reads alignment.'''
    #regex to create two list, one contains cigar string numbers, the other has its letters
    cigar_nums = re.findall("\d+", cigar)
    cigar_lets = re.findall("[A-Z]", cigar)
    print(cigar)
    print(cigar_lets)
    print(cigar_lets[1:])
    print(cigar_nums)

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

print(fix_pos(100, "2S75M", True))