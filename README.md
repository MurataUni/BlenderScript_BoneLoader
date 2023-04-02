Boneを操作するBlender用スクリプト
====

This software is released under the Apache License 2.0, see LICENSE.txt.

## Description

以下の機能を実装
* BlenderのBoneをjson形式で出力
* json形式のファイルを読み込んでBlenderのBoneを生成
* BlenderのBoneにSTLファイルを紐付ける

## Requirement

Blender上で実行する必要がある

## Usage

1. Blenderを起動し、Text Editorを開く
1. Text Editorでblender_script.pyを読み込む
1. 利用したい機能に合わせてファイル下部のコメントアウトを外す
1. ファイル名またはフォルダ名を適切に設定
1. blender_script.pyを実行する

補足：
* importを利用する場合にはあらかじめArmatureを追加しておく必要がある
* stlファイルのBoneへの紐付けを行う場合には各stlのファイル名はBone名と同じにする必要がある
