t = """admiring: With respect and reverence, often used when expressing regard or affection for someone or something. You're amazing.
amused: Light-hearted and typically signaling laughter or enjoyment of a situation. Haha, go for it.
angry: Expresses strong displeasure or rage, often characterized by sharp, harsh or loud expressions. This is stupid.
annoyed: Conveys irritation or frustration, less intense than anger but often tinged with impatience. You're wasting my time.
approving: Suggests agreement or validation, usually conveying acceptance and positivity towards subject. That is a fitting match.
aware: Indicates an understanding or consciousness about the subject.
confident: Exudes certainty and assurance, often assertive and conveying belief. We're proud of this work.
confused: Conveys uncertainty or bewilderment, often with a lack of understanding or clarity about a situation. I have no idea what's going on.
curious: Questioning and often signaling an eagerness to learn or know more about something. Can you please tell me more?
eager: With enthusiasm and keenness, often characterized by anticipation or readiness to engage.
disappointed: Expresses a sense of letdown or dissatisfaction when expectations are not met. This is not as good as I expected.
disapproving: Conveys a negative judgment, criticism, or dissatisfaction towards a subject or action. This is not as good as it should be.
embarrassed: Shows feelings of self-consciousness, shame, or awkwardness, often after a mistake or awkward situation. I felt so self-conscious and awkward.
excited: Full of enthusiasm and anticipation, often showing high energy and eagerness about an event or idea. Looking forward to it!
fearful: Conveys apprehension, anxiety, or dread, often used when there's a perceived threat or danger. I'm scared to death.
grateful: Expresses appreciation or thankfulness, often for someone's actions or presence. Thank you so much.
joyful: Exudes happiness, delight, or pleasure, often full of positive energy and cheerfulness. What a beautiful day to be alive!
loving: Expresses affection, warmth, and tenderness, often used when expressing feelings of affection and care.
mournful: Reveals sorrow or grief, often used when lamenting a loss or a tragic event. I'm sorry for your loss.
neutral: Maintains an objective or impartial attitude; devoid of strong emotions or bias. We'll be there in 20 minutes.
optimistic: Conveys hopefulness and confidence about the outcome of something. The future is full of promise.
relieved: Conveys a sense of release from stress or worry, often following a resolution or good news. That makes me feel so much better.
remorseful: Expresses regret or guilt over a past action or event, often accompanied by a desire to make amends. I'm sorry about that.
repulsed: Conveys a strong aversion or disgust towards a subject or situation. Yuck, get it away!
sad: Expresses unhappiness, sorrow, or grief, generally less intense than mournful but still conveying a negative emotional state. I feel so miserable.
worried: Conveys unease or concern, often anticipating potential problems or negative outcomes.
surprised: Expresses shock or astonishment, usually as a result of an unexpected event or piece of information. Wow, that's so unexpected!
sympathetic: Shows understanding and compassion towards someone else's situation or feelings. I can only imagine what you're going through.
"""
r = []
for l in t.split("\n"):
    r.append(l[:l.find(":")])

print(r)

# ['admiring', 'amused', 'angry', 'annoyed', 'approving', 'aware', 'confident', 'confused', 'curious', 'eager', 'disappointed', 'disapproving', 'embarrassed', 'excited', 'fearful', 'grateful', 'joyful', 'loving', 'mournful', 'neutral', 'optimistic', 'relieved', 'remorseful', 'repulsed', 'sad', 'worried', 'surprised', 'sympathetic']