

# Bookroll PDF Downloader!

由於bookroll實在太難用了，平時閒置一下就要重登入，用手機看著bookroll網頁上的教材也很憋屈，期中考前個晚上還會掛掉....
所以就用python寫了一個小工具，批量下載任何教材的pdf，如此即可離線使用更方便的工具來查看教材，一勞永逸。

由於只有在微積分這門課有用到bookroll，目前僅支援微積分
因為測試帳號不夠，所以如果有bug還請立刻issue!
如果未來我其他課需要用bookroll下載上課資源，將會再更新

# Screenshot

![1](https://raw.githubusercontent.com/lebr0nli/bookroll_pdf_downloader/main/sample1.png)




![2](https://raw.githubusercontent.com/lebr0nli/bookroll_pdf_downloader/main/sample2.png)

#  Requirements

* beautifulsoup4
* requests
* 
		pip install -r requirements.txt

或使用下面另一個辦法

# Google Colab

電腦不需安裝python，直接用google colab開啟**colab_downloader.ipynb**，在左方點選掛載google drive（建議使用ncu gsuite帳號，無限空間真的讚），照順序執行程式即可將檔案存到雲端硬碟。

# Usage

不管是用pc上的python或是colab
共有3次需要使用者輸入的地方

1. 學號
2. brpt bookroll 的密碼
（雖然大家都知道形同虛設，但避免外校人士使用導致版權問題，故請大家自行輸入並下載，下載下來的檔案也請自用就好）
3. 想下載的教材 

關於教材的下載選擇有三種輸入格式：

	1 2 3 9 10
代表下載編號為1 2 3 9 10的教材

	-5 -7
代表下載**除了**編號為5 7的教材

	all
代表下載**所有**教材(微積分共4GB喔)，建議搭配系館網路服用


# 注意

下載下來的pdf僅供學術研究使用，請尊重著作權!
違反著作權後果自負！