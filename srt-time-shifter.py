#!/usr/bin/env python3
# 
# Timeshift the subtitles in a .srt file
# Vivek Sant
# July 2009
# 


import sys
import datetime


# Usage
def usage(args):
  print('''If your subtitles appear too soon or too late, use \
this program to timeshift them.\n
Usage:
    %s subtitles_file.srt seconds [ms]
    %s subtitles_file.srt seconds ms start_title_num
seconds [and ms] should be integers, and can be either positive or negative''' % (args[0], args[0]), file=sys.stderr)
  return 2


#  Parse a file into distinct chunks
def import_parse_file(file):
  chunks = []
  chunk = {}
  i = 0
  for line in open(file, 'r'):
    # If we hit blank line, write out chunk, and reinit empty values
    if line.strip() == '':
      chunks.append(chunk)
      chunk = {}
      i = 0
      continue
    
    if i == 0:
      chunk['num']   = line
    elif i == 1:
      chunk['times'] = line
    elif i == 2:
      chunk['text']  = line
    else:
      chunk['text'] += line
    
    i += 1
  
  # Append last chunk if we didn't get it (if last line of file is not blank)
  if chunk:
    chunks.append(chunk)
  
  return chunks


# Write out a set of chunks to a file
def write_chunks(chunks, out):
  fp = open(out, 'w')
  for chunk in chunks:
    fp.write(chunk['num'])
    fp.write(chunk['times'])
    fp.write(chunk['text'])
    fp.write('\n')
  fp.close()



def parse_add_time(time_str, shift):
  if ',' not in time_str:
    (hms,ms) = (time_str, 0)
  else:
    (hms,ms) = time_str.split(',')
  (h,m,s)  = hms.split(':')
  (s_shift, ms_shift) = shift.split(',')
  old_time = datetime.datetime(1,1,1, int(h), int(m), int(s), int(ms)*1000)
  new_time = old_time + datetime.timedelta(0,int(s_shift),0,int(ms_shift))
  timestamp = str(new_time.time())
  return timestamp.replace('.',',')[0:12]


# Return a set of chunks with times shifted by 's,ms'
# [optionally only starting from frame # <start>]
def time_shift(chunks, shift, start=1):
  chunkCounter = start
  newChunks = []
  for chunk in chunks:
    if int(chunk['num']) >= start:
      (t1, t2) = chunk['times'].split(' --> ')
      try:
        t1 = parse_add_time(t1, shift)
        t2 = parse_add_time(t2, shift)
      except Exception as e:
        # the new timestamp could be invalid
        # discarding the chunk
        continue;

      chunk['times'] = "%s --> %s\n" % (t1,t2)
      chunk['num'] = str(chunkCounter)+"\n";
      chunkCounter = chunkCounter + 1
    newChunks.append(chunk)
  return newChunks


def main(args):
  if len(args) not in [3, 4, 5]:
    return usage(args)

  # Read in args
  file  = args[1]
  out   = file + '.translated'
  start = 1
  if len(args) == 3:
    shift = args[2] + ',000'
  else:
    shift = args[2] + ',' + args[3]
    if len(args) == 5:
      start = int(args[4])

  # Parse chunks from file, shift them, then write out
  chunks = import_parse_file(file)
  chunks = time_shift(chunks, shift, start)
  write_chunks(chunks, out)


if __name__ == '__main__':
  sys.exit(main(sys.argv))
