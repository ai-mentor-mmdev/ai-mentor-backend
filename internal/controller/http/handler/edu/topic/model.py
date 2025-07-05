class DownloadTopicContentBody:
    content_type: str #edu-plan, intro
    topic_id: str

class DownloadBlockContentBody:
    topic_id: str
    block_id: str