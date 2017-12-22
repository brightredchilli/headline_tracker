#!/usr/bin/awk -f

# Awk program to add the images path. Note the hardcoded /images path
BEGIN {
  inside_location_block=0
  location_block_end=0
  finished=0
}

/[:space:]*location.*\{/ {
  inside_location_block=1
}

/[:space:]*}/ {
  if (inside_location_block) {
    location_block_end=NR
  }
}

{
  # Always print the line that was there before
  print

  # after the first location block, write our location block
  if (inside_location_block && NR == location_block_end && finished == 0) {
    print "    ### This location block written by nginx_insert_static.awk"
    print "    location /images/ {"
    print "        root /;"
    print "    }"
    print "    ### End nginx_insert_static.awk"
    finished = 1
  }
}
