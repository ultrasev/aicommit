from manim import *
from manima.functools import center, right, left, down, up
from manima.mobjects import load_image, CurvedLine

DIFF = '''diff --git a.svg b.svg
new file mode 100644
index 0000000..430e467
--- /dev/null
+++ .........
@@ -0,0 +1,39 @@
+<?xml x.....xx>
+<path d....xx>
...
(42 more lines)
'''


class Workflow(Scene):
    def construct(self):
        gitadd = Text("git add src/",
                      color=BLUE_B,
                      font='Courier New'
                      ).scale(0.7).to_edge(UL)
        gitdiff = Text("git diff --cached",
                       color=random_bright_color(),
                       font='Courier New'
                       ).scale(0.7).next_to(gitadd, DOWN).align_to(gitadd, LEFT)
        content = Text(DIFF,
                       font='Courier New',
                       ).scale(0.5).next_to(
            gitdiff, DOWN).align_to(gitdiff, LEFT).shift(RIGHT*0.3)
        self.play(Write(gitadd),
                  run_time=1)
        self.wait(1)
        self.play(Write(gitdiff),
                  run_time=1)

        self.play(Write(content),
                  run_time=1)

        self.wait(1)
        openai = ImageMobject(
            'public/openai.png').scale(0.3).shift(UP*3 + RIGHT*3)
        line = CurvedLine(right(content), left(openai))
        self.play(FadeIn(openai),
                  Circumscribe(content, color=BLUE_C),
                  Create(line),
                  FadeOut(content.copy(), target_position=left(
                      openai), scale=0.1),
                  run_time=2)

        choices = '''1. feat: add new feature
2. fix: bug fix
3. feat: new feature on gpt implementation
4. chore: update build tasks
5. feat: xxx '''.split('\n')
        choices_text = VGroup(
            *[Text(c).scale(0.6) for c in choices]
        )
        choices_text.arrange(DOWN, aligned_edge=LEFT).next_to(
            openai, DOWN, buff=3)
        line2 = Arrow(start=openai.get_bottom(), end=choices_text.get_top(),
                      color=BLUE_C)
        self.play(Write(choices_text),
                  Create(line2),
                  run_time=1)

        self.wait(1)
        self.play(
            Circumscribe(choices_text[2]),
            run_time=2
        )
        t = '''git commit -m xxx'''
        gitcommit = Text(t,
                         color=GREEN,
                         font='Courier New',
                         weight=BOLD
                         ).scale(0.7).next_to(content, DOWN*3).align_to(gitadd, LEFT)

        self.play(
            Transform(choices_text[2], gitcommit),
        )

        self.wait(5)
