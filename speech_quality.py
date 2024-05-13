import flet as ft

#message0=['1: よくわかる', '1.5: 「1:よくわかる」と「2:ときどきわからない語がある」の間', '2: ときどきわからない語がある', '2.5: 「2:ときどきわからない語がある」と「3:聞き手が話題を知っていればわかる」の間', 
#          '3: 聞き手が話題を知っていればわかる', '3.5: 「3:聞き手が話題を知っていればわかる」と「4:ときどきわかる語がある」の間', '4: ときどきわかる語がある', 
#          '4.5: 「4:ときどきわかる語がある」と「5:全くの了解不能」の間', '5: 全くの了解不能']
message0=['1: よくわかる', '2: ときどきわからない語がある', 
          '3: 聞き手が話題を知っていればわかる', '4: ときどきわかる語がある', 
          '5: 全くの了解不能']
message1=['1: 全くの自然である（不自然な要素がない）', '2: やや不自然な要素がある', '3: 明らかに不自然である', '4: 顕著に不自然である', '5: 全く不自然である（自然な要素がない）']
#message2=['-3: 不自然なほど速い', '-2: かなり速い', '-1: やや速い', '0: 自然な速さである', '1: ややゆっくりしている', '2: かなりゆっくりしている', '3: 不自然なほどゆっくりしている']
message2=['-2: 速い', '-1: やや速い', '0: 自然な速さである', '1: ややゆっくりしている', '2: ゆっくりしている',]

class SliderComponent(ft.UserControl):

    def __init__(self, title, message, min=1.0, max=5.0, value=1.0, divisions=8):
        super().__init__()
        self.title = ft.Text(
            spans=[
                ft.TextSpan(title,
                            ft.TextStyle(size=16, weight=ft.FontWeight.BOLD))
            ]
        )
        self.message = message
        self.divisions=divisions
        self.min=min
        self.max=max
        self.value=value

    def build(self):
        self.slider_selected_value = self.value
        self.slider_status = ft.Text(self.get_message(self.slider_selected_value))

        return ft.Container(
            ft.Column([
                self.title,
                ft.Slider(
                    min=self.min,
                    max=self.max,
                    value=self.value,
                    adaptive=False,
                    divisions=self.divisions,
                    active_color=ft.colors.BLUE,
                    thumb_color=ft.colors.BLUE,
                    on_change_start=self.handle_change_start,
                    on_change_end=self.handle_change_end,
                    on_change = self.handle_change,
                    round=1,
                    label='{value}'
                ),
                self.slider_status
            ])
        )

    def get_message(self, value):
        if self.divisions == 8:
            return self.message[int(value * 2)-2]
        elif self.divisions == 6:
            return self.message[int(value) + 3]
        else:
            return self.message[int(value - 1)]
        
        
    def handle_change_start(self, e):
        try:
            self.slider_status.value = self.get_message(e.control.value)
            self.slider_selected_value = e.control.value
            self.slider_status.update()
        except:
            pass
        print(self.slider_selected_value)

    def handle_change_end(self, e):
        self.slider_status.value = self.get_message(e.control.value)
        self.slider_selected_value = e.control.value
        self.slider_status.update()
        print(self.slider_selected_value)

    def handle_change(self, e):
        self.slider_status.value = self.get_message(e.control.value)
        self.slider_selected_value = e.control.value
        self.slider_status.update()
        print(self.slider_selected_value)

def main(page: ft.Page):
   component1 = SliderComponent('明瞭度', message0, min=1, max=5, divisions=4)
   component2 = SliderComponent('声の大きさ', message1, min=1, max=5, divisions=4)
   component3 = SliderComponent('抑揚（全体の音の高低）', message1, min=1, max=5, divisions=4) 
   component4 = SliderComponent('アクセント（単語レベルの音の高低）', message1, min=1, max=5, divisions=4) 
   #component5 = SliderComponent('速さ', message2, min=-2, max=2, value=0.0, divisions=4) 

   page.title = 'Quality Test'
   page.vertical_alignment = ft.MainAxisAlignment.CENTER
   page.add(component1)
   page.add(ft.Divider(height=10, thickness=2))
   page.add(component2)
   page.add(ft.Divider(height=10, thickness=2))
   page.add(component3)
   page.add(ft.Divider(height=10, thickness=2))
   page.add(component4)
   #page.add(ft.Divider(height=10, thickness=2))
   #page.add(component5)

if __name__=="__main__":
    ft.app(target=main)