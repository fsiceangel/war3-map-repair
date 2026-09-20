"""Independent raw MPQ block preservation check (mpyq table decoder)."""
import tempfile
from pathlib import Path
import mpyq
HASH_NAME_A, HASH_NAME_B = 1, 2
_table = None


def crypt_table():
    global _table
    if _table is None:
        seed = 0x00100001
        t = [0] * 0x500
        for i in range(0x100):
            idx = i
            for _ in range(5):
                seed = (seed * 125 + 3) % 0x2AAAAB
                t1 = (seed & 0xFFFF) << 0x10
                seed = (seed * 125 + 3) % 0x2AAAAB
                t2 = seed & 0xFFFF
                t[idx] = t1 | t2
                idx += 0x100
        _table = t
    return _table


def to_bytes(name):
    if isinstance(name, bytes):
        return name
    try:
        return name.encode('ascii')
    except UnicodeEncodeError:
        return name.encode('gbk', 'replace')


def hash_bytes(name, hash_type):
    """StormLib HashString on raw bytes: ASCII upper-cased, '/' mapped to '\\', other bytes unchanged."""
    t = crypt_table()
    seed1 = 0x7FED7FED
    seed2 = 0xEEEEEEEE
    for ch in to_bytes(name):
        if 97 <= ch <= 122:
            ch -= 32
        if ch == 47:
            ch = 92
        value = t[(hash_type << 8) + ch]
        seed1 = (value ^ (seed1 + seed2)) & 0xFFFFFFFF
        seed2 = (ch + seed1 + seed2 + (seed2 << 5) + 3) & 0xFFFFFFFF
    return seed1



def verify(before, after, allowed):
    data = [Path(p).read_bytes() for p in (before, after)]
    offsets = [d.index(b'MPQ\x1a') for d in data]
    if data[0][:offsets[0]] != data[1][:offsets[1]]:
        raise ValueError('Map user header changed')
    raw = [d[o:] for d,o in zip(data,offsets)]
    with tempfile.TemporaryDirectory() as folder:
        archives = []
        for i,d in enumerate(raw):
            p = Path(folder)/str(i); p.write_bytes(d)
            a = mpyq.MPQArchive(str(p), listfile=False)
            a.file.close(); archives.append(a)
        a,b = archives
        exempt = {(hash_bytes(n,HASH_NAME_A),hash_bytes(n,HASH_NAME_B)) for n in set(allowed)|{'(listfile)','(attributes)'}}
        newentries = {(e.hash_a,e.hash_b,e.locale,e.platform):e for e in b.hash_table if e.block_table_index < len(b.block_table)}
        checked = set()
        for e in a.hash_table:
            i=e.block_table_index
            if i >= len(a.block_table) or (e.hash_a,e.hash_b) in exempt: continue
            key=(e.hash_a,e.hash_b,e.locale,e.platform)
            if key not in newentries: raise ValueError('Untouched archive entry disappeared')
            ne=newentries[key]; x=a.block_table[i]; y=b.block_table[ne.block_table_index]
            if x != y: raise ValueError('Untouched block metadata changed')
            if raw[0][x.offset:x.offset+x.archived_size] != raw[1][y.offset:y.offset+y.archived_size]:
                raise ValueError('Untouched compressed bytes changed')
            checked.add(i)
        # Include live orphan blocks as well; no compaction/reindexing is permitted.
        exempt_indices={e.block_table_index for e in a.hash_table if (e.hash_a,e.hash_b) in exempt}
        for i,x in enumerate(a.block_table):
            if i in checked or i in exempt_indices or not x.flags & 0x80000000: continue
            y=b.block_table[i]
            if x != y or raw[0][x.offset:x.offset+x.archived_size] != raw[1][y.offset:y.offset+y.archived_size]:
                raise ValueError('Unreferenced original block changed')
            checked.add(i)
        return len(checked)
