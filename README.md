Unguard
=======

Command-line tool to decipher logs of Java application obfuscated by ProGuard

Usage:

  unguard -m proguard_mapping_file.txt --output deciphered.log obfuscated.log

Limitations
-----------

Python 2.7 is target platform, Python 3 support is planned to be added later.

Only class and method names are processed. No plans to do deobfuscation of field names and annotations.

False deobfuscation of names can occur. In fact it is hard to tell difference between
a.a.a.a.a.b and a.a.a.a.a.b. Even if it is clear for a human that the former is method b in class a.a.a.a.a and
the latter one is a class b in package a.a.a.a.a. I think you got the point.
