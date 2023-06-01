import re

input_file = "Hsapiens_Pure_lncrnas.gtf.fasta"
output_file = "Hsapiens_Pure_lncrnas.gtf.headerreplaced.fasta"
organism_name = "Human"

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        if line.startswith(">"):
            # Extract the original header without the leading ">"
            original_header = line[1:].strip()
            match = re.search(r'TCONS_\d+', original_header)
            header_got = match.group(0)
            # Generate the new header by appending the organism name
            new_header = ">" + header_got + "_" + organism_name
            
            # Write the new header to the output file
            outfile.write(new_header + "\n")
        else:
            # Write the sequence lines as they are
            outfile.write(line)
