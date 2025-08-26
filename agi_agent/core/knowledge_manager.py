"""
Knowledge management system for the AGI Agent.
Handles storage, retrieval, and organization of knowledge.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class KnowledgeItem:
    """Represents a piece of knowledge."""
    id: str
    content: str
    category: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    confidence: float = 1.0
    source: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeItem':
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class KnowledgeManager:
    """
    Manages the agent's knowledge base.
    """
    
    def __init__(self, base_path: str = "./knowledge"):
        self.base_path = base_path
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.logger = logging.getLogger(__name__)
        
        # Ensure knowledge directory exists
        os.makedirs(base_path, exist_ok=True)
        
        # Load existing knowledge
        self._load_knowledge()
    
    def _load_knowledge(self):
        """Load knowledge from storage."""
        knowledge_file = os.path.join(self.base_path, "knowledge.json")
        
        try:
            if os.path.exists(knowledge_file):
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item_data in data.get('items', []):
                    item = KnowledgeItem.from_dict(item_data)
                    self.knowledge_items[item.id] = item
                
                self.logger.info(f"Loaded {len(self.knowledge_items)} knowledge items")
        
        except Exception as e:
            self.logger.error(f"Error loading knowledge: {e}")
    
    def _save_knowledge(self):
        """Save knowledge to storage."""
        knowledge_file = os.path.join(self.base_path, "knowledge.json")
        
        try:
            data = {
                "items": [item.to_dict() for item in self.knowledge_items.values()],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error(f"Error saving knowledge: {e}")
    
    def add_knowledge(self, content: str, category: str, tags: List[str] = None, 
                     source: str = "agent", confidence: float = 1.0) -> str:
        """Add new knowledge item."""
        import uuid
        
        item_id = str(uuid.uuid4())
        now = datetime.now()
        
        item = KnowledgeItem(
            id=item_id,
            content=content,
            category=category,
            tags=tags or [],
            created_at=now,
            updated_at=now,
            confidence=confidence,
            source=source
        )
        
        self.knowledge_items[item_id] = item
        self._save_knowledge()
        
        self.logger.info(f"Added knowledge item: {item_id}")
        return item_id
    
    def get_knowledge(self, item_id: str) -> Optional[KnowledgeItem]:
        """Get knowledge item by ID."""
        return self.knowledge_items.get(item_id)
    
    def search_knowledge(self, query: str, category: str = None, 
                        tags: List[str] = None, limit: int = 10) -> List[KnowledgeItem]:
        """Search knowledge items."""
        results = []
        query_lower = query.lower()
        
        for item in self.knowledge_items.values():
            # Check category filter
            if category and item.category != category:
                continue
            
            # Check tags filter
            if tags and not any(tag in item.tags for tag in tags):
                continue
            
            # Check content match
            if query_lower in item.content.lower():
                results.append(item)
        
        # Sort by confidence and recency
        results.sort(key=lambda x: (x.confidence, x.updated_at), reverse=True)
        
        return results[:limit]
    
    def update_knowledge(self, item_id: str, content: str = None, 
                        tags: List[str] = None, confidence: float = None) -> bool:
        """Update existing knowledge item."""
        if item_id not in self.knowledge_items:
            return False
        
        item = self.knowledge_items[item_id]
        
        if content is not None:
            item.content = content
        if tags is not None:
            item.tags = tags
        if confidence is not None:
            item.confidence = confidence
        
        item.updated_at = datetime.now()
        self._save_knowledge()
        
        return True
    
    def delete_knowledge(self, item_id: str) -> bool:
        """Delete knowledge item."""
        if item_id in self.knowledge_items:
            del self.knowledge_items[item_id]
            self._save_knowledge()
            return True
        return False
    
    def get_categories(self) -> List[str]:
        """Get all knowledge categories."""
        categories = set()
        for item in self.knowledge_items.values():
            categories.add(item.category)
        return sorted(list(categories))
    
    def get_tags(self) -> List[str]:
        """Get all knowledge tags."""
        tags = set()
        for item in self.knowledge_items.values():
            tags.update(item.tags)
        return sorted(list(tags))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        categories = {}
        total_items = len(self.knowledge_items)
        
        for item in self.knowledge_items.values():
            categories[item.category] = categories.get(item.category, 0) + 1
        
        return {
            "total_items": total_items,
            "categories": categories,
            "total_categories": len(categories),
            "total_tags": len(self.get_tags())
        }
    
    async def close(self):
        """Close knowledge manager and save data."""
        self._save_knowledge()
        self.logger.info("Knowledge manager closed")
