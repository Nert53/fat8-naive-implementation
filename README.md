# FAT8 naive implementation
If you dont know what FAT is, you can read it for example [on this wiki page](https://en.wikipedia.org/wiki/File_Allocation_Table). The 8 in the name means that 8 bits are reserved for one record in table.

### Implementation
This task was final for subject "Operating System 2" on Department of Science on Palacky University in Olomouc.
You can find the task description in file `zapocet-zadani.pdf` or on [Petr Krajca's page](https://phoenix.inf.upol.cz/~krajcap/courses/2023ZS/OS2/) (it is in czech).
For disk I choose the second option with classic read/write operations and making another layer over it for caching.

### Using script
Demonstration of how it works can be find in `main.py`. Or you can test it on your own by calling methods as are 
descripted in pdf file. For viewing the "disk" I recommend some hex dump editor
(in my case it was extesion `BinEd - Binary/Hex Editor from Miroslav Hajda`).

 
