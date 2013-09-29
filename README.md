Unguard
=======

Command-line tool to decipher logs of Java application obfuscated by proguard

Usage:

  unguard -m proguard_mapping_file.txt --output deciphered.log obfuscated.log

Limitations
-----------

False deobfuscation of names can be an issue. In fact it is hard to tell difference between
a.a.a.a.a.b and a.a.a.a.a.b. Even if it is clear for a human that the former is method b in class a.a.a.a.a and
the latter one is a class b in package a.a.a.a.a. I think you got the point.
