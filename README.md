# VideoLabelTool
A label-tool of continuous frames developed by pyqt5

## Description
We can use hand-annotations(mouse) of 1.png and 10.png to auto generate interpolated-annotations of 2~9.png.  
We also can hand-annotate a image has already interpolated-annotated to adjust its bbox ,and a new
hand-annotation will start a new interpolation job at a mean time.

![image](https://github.com/nat99up/VideoLabelTool/blob/master/util/Demo.gif)

* Blue bbox : hand-annotation
* Yellow bbox : interpolated-annotation

## Hotkeys
| Key        | function                                   |
| ---------- | ------------------------------------------ |
| →          | Next image                                 |
| ←          | Previous image                             |
| s          | Save to .crop file                         |
| l          | Load from .crop file                       |
| >          | 10 Next image                              |
| <          | 10 Previous image                          |
| e          | Change all blue bbox to yellow bbox        |
| c          | Cancel bbox (two step cancel:start & end point)|
| q          | Leave                                      |


## Usage
```
python3 cropTool.py -d [directory of images]
```

* example
```
python3 cropTool.py -d data/example/
# output file = data/example.crop
# each row in .crop file = [filename] [x1] [y1] [x2] [y2]
```