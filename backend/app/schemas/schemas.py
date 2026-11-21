try:
    from pydantic import BaseModel, Field
    from typing import Optional, List, Dict, Any
except ImportError:
    # Lightweight fallback for environments where pydantic is not yet installed
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__
    def Field(default=None, **kwargs):
        return default
    from typing import Optional, List, Dict, Any

# AI Provider Schemas
class AIProviderBase(BaseModel):
    name: str
    provider_type: str
    api_endpoint: Optional[str] = ""
    model: str
    image_model: Optional[str] = ""
    is_enabled: Optional[bool] = True
    is_default: Optional[bool] = False
    is_fallback: Optional[bool] = False

class AIProviderCreate(AIProviderBase):
    api_key: Optional[str] = ""

class AIProviderUpdate(BaseModel):
    name: Optional[str] = None
    provider_type: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    image_model: Optional[str] = None
    is_enabled: Optional[bool] = None
    is_default: Optional[bool] = None
    is_fallback: Optional[bool] = None

class AIProviderOut(BaseModel):
    id: int
    name: str
    provider_type: str
    api_endpoint: Optional[str]
    masked_key: str
    model: str
    image_model: Optional[str]
    is_enabled: bool
    is_default: bool
    is_fallback: bool
    status: str
    error_message: Optional[str]
    last_tested_at: Optional[str]

# Image Provider Schemas
class ImageProviderCreate(BaseModel):
    name: str
    provider_type: str
    api_endpoint: Optional[str] = ""
    api_key: Optional[str] = ""
    model: Optional[str] = ""
    aspect_ratio: Optional[str] = "1:1"
    resolution: Optional[str] = "1024x1024"
    style: Optional[str] = "photorealistic documentary"
    negative_prompt: Optional[str] = ""
    is_enabled: Optional[bool] = True
    is_default: Optional[bool] = False
    is_fallback: Optional[bool] = False

class ImageProviderUpdate(BaseModel):
    name: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    aspect_ratio: Optional[str] = None
    resolution: Optional[str] = None
    style: Optional[str] = None
    negative_prompt: Optional[str] = None
    is_enabled: Optional[bool] = None
    is_default: Optional[bool] = None
    is_fallback: Optional[bool] = None

# Facebook Config Schemas
class FacebookConfigUpdate(BaseModel):
    page_id: Optional[str] = None
    page_name: Optional[str] = None
    page_access_token: Optional[str] = None
    user_access_token: Optional[str] = None

class FacebookTestPost(BaseModel):
    message: str
    image_url: Optional[str] = None

# Caption Template Schemas
class CaptionTemplateCreate(BaseModel):
    name: str
    hook_style: Optional[str] = "shocking_fact"
    caption_length: Optional[str] = "documentary"
    storytelling_format: Optional[str] = "deep_dive"
    language: Optional[str] = "en"
    emoji_usage: Optional[str] = "moderate"
    hashtag_quantity: Optional[int] = 10
    cta_style: Optional[str] = "follow_page"
    brand_voice: Optional[str] = "dramatic"
    ending_line: Optional[str] = ""
    is_default: Optional[bool] = False

class CaptionTemplateUpdate(BaseModel):
    name: Optional[str] = None
    hook_style: Optional[str] = None
    caption_length: Optional[str] = None
    storytelling_format: Optional[str] = None
    language: Optional[str] = None
    emoji_usage: Optional[str] = None
    hashtag_quantity: Optional[int] = None
    cta_style: Optional[str] = None
    brand_voice: Optional[str] = None
    ending_line: Optional[str] = None
    is_default: Optional[bool] = None

# Topic Schemas
class TopicCreate(BaseModel):
    category: str
    title: str
    prompt_seed: Optional[str] = ""

class TopicUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    prompt_seed: Optional[str] = None
    is_active: Optional[bool] = None

# Schedule Schemas
class ScheduleSlotUpdate(BaseModel):
    slot_number: int
    post_time: str
    category_preference: Optional[str] = "Any"
    caption_template_id: Optional[int] = None
    is_enabled: Optional[bool] = True

class ScheduleBatchUpdate(BaseModel):
    slots: List[ScheduleSlotUpdate]

# Post Generation and Management
class GenerateRequest(BaseModel):
    category: Optional[str] = None
    topic: Optional[str] = None
    language: Optional[str] = "en"
    template_id: Optional[int] = None
    ai_provider_id: Optional[int] = None
    image_provider_id: Optional[int] = None
    publish_now: Optional[bool] = False

class PostUpdate(BaseModel):
    headline: Optional[str] = None
    caption: Optional[str] = None
    hashtags: Optional[str] = None
    image_url: Optional[str] = None
    scheduled_for: Optional[str] = None
    status: Optional[str] = None
