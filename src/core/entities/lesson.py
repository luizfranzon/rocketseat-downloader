from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Download:
    title: str
    file_url: str


@dataclass
class Lesson:
    title: str
    group_title: str
    resource: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    author: Optional[str] = None
    downloads: list[Download] = field(default_factory=list)


@dataclass
class Group:
    title: str
    lessons: list[Lesson] = field(default_factory=list)


@dataclass
class Module:
    title: str
    type: str = ""
    slug: Optional[str] = None
    cluster_slug: Optional[str] = None


@dataclass
class Specialization:
    title: str
    slug: str
