from os.path import split

xp1_groups = '1,4,20,22,23,29,30,32,34,35,42,44,45,46,49,50,51,52,53,54,55,56,57,58,59,60'
xp2_groups = '2,12,13,14,15,31,33,41'
xp3_groups = '9,27,37'
xp4_groups = '3,5,6,7,8,10,11,16,17,18,19,21,24,25,26,28,36,38,39,40,43,47,48'


stage1 = '3,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,1,1,0,0,0,0,0,3,3,0,1,0,3,3,0,0,0,0,0,0,1,0,1,1,3,0,0,3,1,1,1,1,1,1,1,1,1,1,1'


print(list(map(int, xp1_groups.split(','))))

print(len(stage1.split(',')))