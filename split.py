from pathlib import Path
import numpy as np

def rm_tree(pth):
    pth = Path(pth)
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()

BASE = Path('waymo_kitti_data/validation4')

calib_dir = BASE / Path('calib')

calibs = calib_dir.glob('*.txt')

EXT_STRING = 'Tr_velo_to_cam:'
EXT_STRING = 'Tr_lidar_to_vehicle:'

calibs = sorted(list(calibs))
prev = np.asarray([0 for _ in range(12)])

sequences = []
sequence_single = []
prev_seq_str = calibs[0].name[0:3]
for idx, calib in enumerate(calibs):
    seq_str = calib.name[0:3]
    if seq_str != prev_seq_str:
        print(prev_seq_str)
        sequences.append(sequence_single)
        sequence_single = []
    sequence_single.append(calib)
    prev_seq_str = seq_str
    
    
# for idx, calib in enumerate(calibs):
#     # print(calib.name)
#     with open(calib, 'r') as f:
#         text = f.read()
#     fnd = text.rfind(EXT_STRING)
#     assert fnd != -1
#     ext_text = text[fnd + len(EXT_STRING) + 1:]
#     ext = map(str.strip, ext_text.split(" "))
#     ext = map(np.float32, ext)
#     ext = np.asarray(list(ext))
#     if np.array_equal(prev, ext):
#         print(calib.name)
#     else:
#         if idx != 0:
#             print(ext)
#             sequences.append(sequence_single)
#             sequence_single = []
#     sequence_single.append(calib)
#     prev = ext

    # if idx > 1000:
    #     break
print(len(sequences))
## Create symlink ##

velo_src_dir = BASE / Path('velodyne')
pose_src_dir = BASE / Path('pose')

for seq_idx, seq in enumerate(sequences):
    seq_dir = BASE.parent / Path('split_validation/' + str(seq_idx).zfill(3) )
    print(seq_dir)
    seq_dir.mkdir(parents=True, exist_ok=True)
    velo_save_dir  = seq_dir / Path('velodyne')
    rm_tree(velo_save_dir)
    velo_save_dir.mkdir(parents=True, exist_ok=True)

    ### Write pose.txt and calib.txt ### 
    # write all pose in a file (with loop all frames)
    pose_save_path = seq_dir / Path('pose.txt')
    calib_save_path = seq_dir / Path('calib.txt')
    
    write_buf = ""
    for ext_path in seq:
        assert ext_path.name[-4:] == '.txt'
        frame_idx = ext_path.name[:-4]
        pose_src_path = pose_src_dir / Path(frame_idx + '.txt')
        with open(pose_src_path, 'r') as pose_src_file:
            pose_text = pose_src_file.read()
            pose = np.asarray(pose_text.split()).reshape(-1)
            pose = np.asarray(list(map(np.float32, pose)))
            # write
            write_buf += pose_text.replace('\n', ' ').strip() + '\n'
    
    with open(pose_save_path, 'w') as pose_save_file:
        pose_save_file.write(write_buf)
                
    # copy one of the calib.txt with rename
    calib_src_path = Path(seq[0])
    with open(calib_src_path, 'r') as calib_src_file:
        calib_text = calib_src_file.read()
    with open(calib_save_path, 'w') as calib_save_file:
        calib_save_file.write(calib_text)

    for ext_path in seq:
        assert ext_path.name[-4:] == '.txt'
        frame_idx = ext_path.name[:-4]
        real_frame_idx = str(frame_idx)[3:].zfill(6)
        velo_path = velo_src_dir / Path(frame_idx + '.bin')
        velo_sym_path = velo_save_dir / Path(real_frame_idx + '.bin')
        if velo_sym_path.exists():
            # velo_sym_path.unlink()
            continue
        velo_sym_path.symlink_to(velo_path.absolute())
        print(frame_idx, velo_sym_path.absolute(), velo_path.absolute())

        
