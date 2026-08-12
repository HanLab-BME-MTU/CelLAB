"""
cintelia Conversation Manager
=============================

Manages conversation history, context pruning, and session persistence.

This module:
- Maintains conversation history across queries
- Prunes old messages to fit context window
- Exports/imports conversation sessions
- Tracks conversation metadata (timestamps, tokens, etc.)
- Provides conversation search and retrieval

Features:
- Rolling window (keeps last N turns)
- Token counting for context limits
- Session persistence (save/load from JSON)
- Conversation search by keyword/date
- Summary generation for long conversations

Author: Han Lab - Mechanobiology Dry Lab
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import re


# ============================================================================
# CONVERSATION MANAGER CLASS
# ============================================================================

class ConversationManager:
    """
    Manage conversation history and context
    
    Handles:
    - Message storage with metadata
    - Context window management
    - Token counting and pruning
    - Session persistence
    - Conversation search
    
    Usage:
        conv = ConversationManager(max_turns=10)
        
        # Add messages
        conv.add_user_message("What is IMMUNIA?")
        conv.add_assistant_message("IMMUNIA is...")
        
        # Get recent history
        history = conv.get_recent_history(n_turns=3)
        
        # Export session
        conv.export_session("session.json")
    """
    
    def __init__(
        self,
        max_turns: int = 10,
        max_tokens: int = 4096,
        session_id: Optional[str] = None
    ):
        """
        Initialize conversation manager
        
        Args:
            max_turns: Maximum conversation turns to keep (1 turn = 2 messages)
            max_tokens: Maximum tokens in context window
            session_id: Unique session identifier (auto-generated if None)
        """
        
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.session_id = session_id or self._generate_session_id()
        
        # Message storage
        self.messages: List[Dict[str, Any]] = []
        
        # Session metadata
        self.metadata = {
            'session_id': self.session_id,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'total_messages': 0,
            'total_turns': 0,
            'model_switches': [],  # Track mode changes
            'context_type_changes': []  # Track context switches
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"
    
    def add_user_message(
        self,
        content: str,
        context_type: Optional[str] = None,
        mode: str = 'local',
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add user message to conversation
        
        Args:
            content: Message content
            context_type: Context type ('immunia', 'fastia', etc.)
            mode: AI mode used ('local' or 'server')
            metadata: Additional metadata
        
        Returns:
            Message ID (index in messages list)
        """
        
        message = {
            'role': 'user',
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'context_type': context_type,
            'mode': mode,
            'tokens': self._estimate_tokens(content),
            'metadata': metadata or {}
        }
        
        self.messages.append(message)
        self.metadata['total_messages'] += 1
        self.metadata['last_updated'] = datetime.now().isoformat()
        
        # Track context changes
        if context_type and (
            not self.metadata['context_type_changes'] or
            self.metadata['context_type_changes'][-1] != context_type
        ):
            self.metadata['context_type_changes'].append(context_type)
        
        return len(self.messages) - 1
    
    def add_assistant_message(
        self,
        content: str,
        mode: str = 'local',
        model_info: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Add assistant message to conversation
        
        Args:
            content: Message content
            mode: AI mode used ('local' or 'server')
            model_info: Model information (name, version, etc.)
            metadata: Additional metadata
        
        Returns:
            Message ID (index in messages list)
        """
        
        message = {
            'role': 'assistant',
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'mode': mode,
            'model_info': model_info or {},
            'tokens': self._estimate_tokens(content),
            'metadata': metadata or {}
        }
        
        self.messages.append(message)
        self.metadata['total_messages'] += 1
        self.metadata['total_turns'] = len([m for m in self.messages if m['role'] == 'user'])
        self.metadata['last_updated'] = datetime.now().isoformat()
        
        # Track mode changes
        if mode and (
            not self.metadata['model_switches'] or
            self.metadata['model_switches'][-1] != mode
        ):
            self.metadata['model_switches'].append(mode)
        
        return len(self.messages) - 1
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        
        Simple heuristic: ~1.3 tokens per word for English
        
        Args:
            text: Input text
        
        Returns:
            Estimated token count
        """
        
        words = len(text.split())
        return int(words * 1.3)
    
    def get_recent_history(
        self,
        n_turns: Optional[int] = None,
        max_tokens: Optional[int] = None,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get recent conversation history
        
        Args:
            n_turns: Number of recent turns (None = use max_turns)
            max_tokens: Maximum tokens to include (None = use max_tokens)
            include_metadata: Include message metadata
        
        Returns:
            List of recent messages
        """
        
        if not self.messages:
            return []
        
        n_turns = n_turns or self.max_turns
        max_tokens = max_tokens or self.max_tokens
        
        # Get last N turns (N turns = 2N messages)
        n_messages = min(n_turns * 2, len(self.messages))
        recent_messages = self.messages[-n_messages:]
        
        # Prune by token count if needed
        pruned_messages = self._prune_by_tokens(recent_messages, max_tokens)
        
        # Format messages
        if include_metadata:
            return pruned_messages
        else:
            return [
                {
                    'role': m['role'],
                    'content': m['content']
                }
                for m in pruned_messages
            ]
    
    def _prune_by_tokens(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int
    ) -> List[Dict[str, Any]]:
        """
        Prune messages to fit token limit
        
        Args:
            messages: List of messages
            max_tokens: Maximum token count
        
        Returns:
            Pruned message list
        """
        
        if not messages:
            return []
        
        # Calculate total tokens
        total_tokens = sum(m['tokens'] for m in messages)
        
        # If under limit, return all
        if total_tokens <= max_tokens:
            return messages
        
        # Otherwise, remove oldest messages until under limit
        pruned = messages.copy()
        while pruned and sum(m['tokens'] for m in pruned) > max_tokens:
            # Remove oldest pair (user + assistant)
            if len(pruned) >= 2:
                pruned = pruned[2:]
            else:
                pruned = pruned[1:]
        
        return pruned
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """
        Get all messages in conversation
        
        Returns:
            Complete message list
        """
        return self.messages.copy()
    
    def get_message_by_id(self, message_id: int) -> Optional[Dict[str, Any]]:
        """
        Get specific message by ID
        
        Args:
            message_id: Message index
        
        Returns:
            Message dictionary or None
        """
        
        if 0 <= message_id < len(self.messages):
            return self.messages[message_id].copy()
        return None
    
    def search_messages(
        self,
        query: str,
        role: Optional[str] = None,
        context_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Tuple[int, Dict[str, Any]]]:
        """
        Search messages by keyword and filters
        
        Args:
            query: Search query (keywords)
            role: Filter by role ('user' or 'assistant')
            context_type: Filter by context type
            start_date: Filter by start date
            end_date: Filter by end date
        
        Returns:
            List of (message_id, message) tuples
        """
        
        results = []
        query_lower = query.lower()
        
        for idx, message in enumerate(self.messages):
            # Role filter
            if role and message['role'] != role:
                continue
            
            # Context type filter
            if context_type and message.get('context_type') != context_type:
                continue
            
            # Date filters
            msg_time = datetime.fromisoformat(message['timestamp'])
            if start_date and msg_time < start_date:
                continue
            if end_date and msg_time > end_date:
                continue
            
            # Keyword search
            if query_lower in message['content'].lower():
                results.append((idx, message.copy()))
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get conversation statistics
        
        Returns:
            Dictionary with statistics
        """
        
        if not self.messages:
            return {
                'total_messages': 0,
                'total_turns': 0,
                'total_tokens': 0,
                'avg_user_tokens': 0,
                'avg_assistant_tokens': 0
            }
        
        user_messages = [m for m in self.messages if m['role'] == 'user']
        assistant_messages = [m for m in self.messages if m['role'] == 'assistant']
        
        user_tokens = [m['tokens'] for m in user_messages]
        assistant_tokens = [m['tokens'] for m in assistant_messages]
        
        stats = {
            'total_messages': len(self.messages),
            'total_turns': len(user_messages),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'total_tokens': sum(m['tokens'] for m in self.messages),
            'avg_user_tokens': sum(user_tokens) / len(user_tokens) if user_tokens else 0,
            'avg_assistant_tokens': sum(assistant_tokens) / len(assistant_tokens) if assistant_tokens else 0,
            'max_user_tokens': max(user_tokens) if user_tokens else 0,
            'max_assistant_tokens': max(assistant_tokens) if assistant_tokens else 0,
            'mode_distribution': self._get_mode_distribution(),
            'context_distribution': self._get_context_distribution()
        }
        
        return stats
    
    def _get_mode_distribution(self) -> Dict[str, int]:
        """Get distribution of messages by mode"""
        distribution = defaultdict(int)
        for message in self.messages:
            mode = message.get('mode', 'unknown')
            distribution[mode] += 1
        return dict(distribution)
    
    def _get_context_distribution(self) -> Dict[str, int]:
        """Get distribution of messages by context type"""
        distribution = defaultdict(int)
        for message in self.messages:
            context = message.get('context_type', 'none')
            if context:
                distribution[context] += 1
        return dict(distribution)
    
    def clear(self):
        """Clear all messages and reset session"""
        self.messages = []
        self.metadata['total_messages'] = 0
        self.metadata['total_turns'] = 0
        self.metadata['model_switches'] = []
        self.metadata['context_type_changes'] = []
        self.metadata['last_updated'] = datetime.now().isoformat()
    
    def export_session(
        self,
        output_path: str,
        include_metadata: bool = True
    ):
        """
        Export conversation session to JSON
        
        Args:
            output_path: Path to output file
            include_metadata: Include session metadata
        """
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        session_data = {
            'messages': self.messages,
            'statistics': self.get_statistics()
        }
        
        if include_metadata:
            session_data['metadata'] = self.metadata
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Session exported to: {output_file}")
    
    def import_session(self, input_path: str):
        """
        Import conversation session from JSON
        
        Args:
            input_path: Path to input file
        """
        
        input_file = Path(input_path)
        
        if not input_file.exists():
            raise FileNotFoundError(f"Session file not found: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Load messages
        self.messages = session_data.get('messages', [])
        
        # Load metadata if available
        if 'metadata' in session_data:
            self.metadata.update(session_data['metadata'])
        
        print(f"✅ Session imported from: {input_file}")
        print(f"   Messages: {len(self.messages)}")
        print(f"   Turns: {self.metadata.get('total_turns', 0)}")
    
    def generate_summary(self, max_length: int = 500) -> str:
        """
        Generate summary of conversation
        
        Args:
            max_length: Maximum summary length in characters
        
        Returns:
            Conversation summary
        """
        
        if not self.messages:
            return "No conversation to summarize."
        
        stats = self.get_statistics()
        
        summary = f"""
Conversation Summary
{'='*50}

Session ID: {self.session_id}
Created: {self.metadata['created_at']}
Duration: {self._calculate_duration()}

Statistics:
- Total turns: {stats['total_turns']}
- Total messages: {stats['total_messages']}
- Total tokens: {stats['total_tokens']}

Topics discussed:
{self._extract_topics()}

Mode usage:
{self._format_distribution(stats['mode_distribution'])}

Context types:
{self._format_distribution(stats['context_distribution'])}
"""
        
        return summary.strip()
    
    def _calculate_duration(self) -> str:
        """Calculate conversation duration"""
        if not self.messages:
            return "0 minutes"
        
        start = datetime.fromisoformat(self.messages[0]['timestamp'])
        end = datetime.fromisoformat(self.messages[-1]['timestamp'])
        duration = end - start
        
        minutes = duration.seconds // 60
        if minutes < 60:
            return f"{minutes} minutes"
        else:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}h {mins}m"
    
    def _extract_topics(self) -> str:
        """Extract main topics from conversation"""
        # Simple keyword extraction
        keywords = defaultdict(int)
        
        technical_terms = {
            'immunia', 'fastia', 'segmentation', 'tracking', 'keller-segel',
            'ccm', 'granger', 'graph', 'network', 'cell', 'tumor', 'nk',
            'focal', 'adhesion', 'parameter', 'threshold', 'error'
        }
        
        for message in self.messages:
            if message['role'] == 'user':
                content = message['content'].lower()
                for term in technical_terms:
                    if term in content:
                        keywords[term] += 1
        
        # Get top 5 topics
        top_topics = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if not top_topics:
            return "- General questions"
        
        return '\n'.join(f"- {topic} ({count} mentions)" for topic, count in top_topics)
    
    def _format_distribution(self, distribution: Dict[str, int]) -> str:
        """Format distribution dictionary as string"""
        if not distribution:
            return "- None"
        
        return '\n'.join(f"- {key}: {value}" for key, value in distribution.items())
    
    def __len__(self) -> int:
        """Get number of messages"""
        return len(self.messages)
    
    def __repr__(self) -> str:
        """String representation"""
        return f"ConversationManager(session={self.session_id}, messages={len(self.messages)}, turns={self.metadata.get('total_turns', 0)})"


# ============================================================================
# TESTING
# ============================================================================

def test_conversation_manager():
    """Test conversation manager"""
    
    print("\n" + "="*60)
    print("💬 Conversation Manager - Test Suite")
    print("="*60 + "\n")
    
    # Initialize
    conv = ConversationManager(max_turns=5)
    print(f"Created: {conv}")
    
    # Add messages
    print("\n" + "-"*60)
    print("Adding test messages...")
    
    conv.add_user_message("What is IMMUNIA?", context_type='general', mode='local')
    conv.add_assistant_message("IMMUNIA is an immune cell analysis pipeline...", mode='local')
    
    conv.add_user_message("How do I segment NK cells?", context_type='immunia', mode='local')
    conv.add_assistant_message("To segment NK cells, adjust these parameters...", mode='local')
    
    conv.add_user_message("I'm getting errors", context_type='error', mode='local')
    conv.add_assistant_message("Let me help diagnose the error...", mode='local')
    
    print(f"Added {len(conv)} messages")
    
    # Get recent history
    print("\n" + "-"*60)
    print("Recent history (last 2 turns):")
    history = conv.get_recent_history(n_turns=2)
    for msg in history:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # Search messages
    print("\n" + "-"*60)
    print("Searching for 'error'...")
    results = conv.search_messages('error')
    print(f"Found {len(results)} matches")
    for idx, msg in results:
        print(f"  [{idx}] {msg['role']}: {msg['content'][:50]}...")
    
    # Statistics
    print("\n" + "-"*60)
    print("Statistics:")
    stats = conv.get_statistics()
    print(json.dumps(stats, indent=2))
    
    # Summary
    print("\n" + "-"*60)
    print("Summary:")
    print(conv.generate_summary())
    
    # Export
    print("\n" + "-"*60)
    print("Exporting session...")
    conv.export_session('test_conversation.json')
    
    # Import test
    print("\n" + "-"*60)
    print("Testing import...")
    conv2 = ConversationManager()
    conv2.import_session('test_conversation.json')
    print(f"Imported: {conv2}")
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    """Run test suite"""
    test_conversation_manager()
