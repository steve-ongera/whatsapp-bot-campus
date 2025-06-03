import random
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from myapplication.models import Message, MessageClassification, ImportantKeyword
# Add missing import at the top
from django.db import models

class Command(BaseCommand):
    help = "Classify existing messages based on keywords, sender role, and ML simulation"

    # Role-based importance weights
    role_weights = {
        'teacher': 0.8,      # Teachers' messages are generally important
        'class_rep': 0.6,    # Class reps send organizational messages
        'student': 0.3       # Students' messages are less likely to be critical
    }

    # Classification methods with their weights for realistic distribution
    classification_methods = {
        'keyword': 0.40,      # 40% keyword-based
        'sender_role': 0.30,  # 30% role-based
        'ml': 0.20,          # 20% ML-based
        'manual': 0.10       # 10% manual classification
    }

    def handle(self, *args, **options):
        # Get all messages that don't have classifications yet
        unclassified_messages = Message.objects.filter(
            messageclassification__isnull=True
        )

        if not unclassified_messages.exists():
            self.stdout.write(self.style.WARNING("No unclassified messages found!"))
            return

        # Get all active keywords for classification
        keywords = ImportantKeyword.objects.filter(is_active=True)
        
        if not keywords.exists():
            self.stdout.write(self.style.WARNING("No keywords found! Run populate_keywords first."))
            return

        self.stdout.write(f"📊 Found {unclassified_messages.count()} messages to classify")
        self.stdout.write(f"🔑 Using {keywords.count()} keywords for classification")

        classified_count = 0
        important_count = 0

        # Process messages in batches for better performance
        with transaction.atomic():
            for message in unclassified_messages:
                classification = self.classify_message(message, keywords)
                
                if classification:
                    classified_count += 1
                    if classification.is_important:
                        important_count += 1
                    
                    # Show progress every 50 messages
                    if classified_count % 50 == 0:
                        self.stdout.write(f"Processed {classified_count} messages...")

        # Final statistics
        self.stdout.write(self.style.SUCCESS(f"\n✅ Classification completed!"))
        self.stdout.write(f"📈 Total messages classified: {classified_count}")
        self.stdout.write(f"⭐ Important messages: {important_count}")
        self.stdout.write(f"📋 Regular messages: {classified_count - important_count}")
        self.stdout.write(f"🎯 Importance rate: {(important_count/classified_count*100):.1f}%")

        # Show detailed statistics
        self.show_classification_statistics()

    def classify_message(self, message, keywords):
        """Classify a single message and return MessageClassification object"""
        
        # Choose classification method based on realistic distribution
        method = self.choose_classification_method()
        
        # Initialize classification data
        detected_keywords = []
        importance_score = 0.0
        confidence_level = 0.0
        is_important = False

        if method == 'keyword':
            # Keyword-based classification
            detected_keywords, importance_score, confidence_level = self.keyword_classification(
                message.content, keywords
            )
            is_important = importance_score >= 0.6

        elif method == 'sender_role':
            # Role-based classification
            importance_score, confidence_level = self.role_based_classification(message.sender.role)
            is_important = importance_score >= 0.6

        elif method == 'ml':
            # Simulated ML classification
            importance_score, confidence_level = self.ml_classification(message.content)
            is_important = importance_score >= 0.5

        elif method == 'manual':
            # Simulated manual classification
            importance_score, confidence_level = self.manual_classification()
            is_important = importance_score >= 0.7

        # Create and save classification
        classification = MessageClassification.objects.create(
            message=message,
            is_important=is_important,
            importance_score=round(importance_score, 2),
            detected_keywords=detected_keywords,
            classification_method=method,
            confidence_level=round(confidence_level, 2)
        )

        return classification

    def choose_classification_method(self):
        """Choose classification method based on realistic distribution"""
        methods = list(self.classification_methods.keys())
        weights = list(self.classification_methods.values())
        return random.choices(methods, weights=weights)[0]

    def keyword_classification(self, content, keywords):
        """Classify message based on keyword matching"""
        detected_keywords = []
        total_weight = 0
        content_lower = content.lower()

        # Find matching keywords
        for keyword in keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(keyword.keyword.lower()) + r'\b'
            if re.search(pattern, content_lower):
                detected_keywords.append({
                    'keyword': keyword.keyword,
                    'category': keyword.category,
                    'weight': keyword.weight
                })
                total_weight += keyword.weight

        # Calculate importance score based on detected keywords
        if detected_keywords:
            # Normalize score based on maximum possible weight (10) and number of keywords
            max_possible = len(detected_keywords) * 10
            importance_score = min(total_weight / max_possible, 1.0)
            confidence_level = min(0.8 + (len(detected_keywords) * 0.1), 0.95)
        else:
            importance_score = 0.1 + random.uniform(0, 0.3)  # Small random score for non-matching
            confidence_level = 0.3 + random.uniform(0, 0.2)

        return detected_keywords, importance_score, confidence_level

    def role_based_classification(self, sender_role):
        """Classify based on sender's role"""
        base_score = self.role_weights.get(sender_role, 0.3)
        
        # Add some randomness
        importance_score = base_score + random.uniform(-0.2, 0.2)
        importance_score = max(0.0, min(1.0, importance_score))
        
        # Confidence is high for role-based classification
        confidence_level = 0.7 + random.uniform(0, 0.2)
        
        return importance_score, confidence_level

    def ml_classification(self, content):
        """Simulate ML-based classification"""
        # Simulate ML algorithm with some realistic patterns
        content_features = {
            'length': len(content),
            'has_question': '?' in content,
            'has_exclamation': '!' in content,
            'has_numbers': any(char.isdigit() for char in content),
            'has_uppercase': any(char.isupper() for char in content),
            'word_count': len(content.split())
        }
        
        # Simulate ML scoring based on features
        score = 0.0
        
        # Longer messages tend to be more important
        if content_features['word_count'] > 15:
            score += 0.3
        elif content_features['word_count'] > 8:
            score += 0.2
        
        # Questions might be important
        if content_features['has_question']:
            score += 0.2
        
        # Exclamations suggest urgency
        if content_features['has_exclamation']:
            score += 0.15
        
        # Numbers might indicate dates, times, scores
        if content_features['has_numbers']:
            score += 0.1
        
        # Add randomness to simulate ML uncertainty
        score += random.uniform(-0.2, 0.3)
        
        importance_score = max(0.0, min(1.0, score))
        confidence_level = 0.5 + random.uniform(0, 0.3)  # ML confidence varies
        
        return importance_score, confidence_level

    def manual_classification(self):
        """Simulate manual classification by humans"""
        # Manual classification tends to be more accurate but subjective
        
        # Simulate human decision-making
        base_scores = [0.1, 0.3, 0.5, 0.7, 0.9]  # Human tends to use round numbers
        importance_score = random.choice(base_scores) + random.uniform(-0.1, 0.1)
        
        # Manual classification has high confidence
        confidence_level = 0.8 + random.uniform(0, 0.15)
        
        return importance_score, confidence_level

    def show_classification_statistics(self):
        """Display detailed classification statistics"""
        self.stdout.write(f"\n📊 CLASSIFICATION STATISTICS:")
        
        # Overall stats
        total = MessageClassification.objects.count()
        important = MessageClassification.objects.filter(is_important=True).count()
        
        self.stdout.write(f"Total classified messages: {total}")
        self.stdout.write(f"Important messages: {important} ({important/total*100:.1f}%)")
        
        # By classification method
        self.stdout.write(f"\n🔍 By classification method:")
        for method, _ in MessageClassification._meta.get_field('classification_method').choices:
            count = MessageClassification.objects.filter(classification_method=method).count()
            important_count = MessageClassification.objects.filter(
                classification_method=method, is_important=True
            ).count()
            percentage = (count / total * 100) if total > 0 else 0
            importance_rate = (important_count / count * 100) if count > 0 else 0
            
            self.stdout.write(f"  {method.title()}: {count} ({percentage:.1f}%) - {importance_rate:.1f}% important")
        
        # By sender role
        self.stdout.write(f"\n👥 By sender role:")
        for role in ['teacher', 'class_rep', 'student']:
            count = MessageClassification.objects.filter(message__sender__role=role).count()
            important_count = MessageClassification.objects.filter(
                message__sender__role=role, is_important=True
            ).count()
            percentage = (count / total * 100) if total > 0 else 0
            importance_rate = (important_count / count * 100) if count > 0 else 0
            
            self.stdout.write(f"  {role.title()}: {count} ({percentage:.1f}%) - {importance_rate:.1f}% important")
        
        # Score distribution
        self.stdout.write(f"\n📈 Importance score distribution:")
        score_ranges = [
            (0.0, 0.2, "Very Low"),
            (0.2, 0.4, "Low"), 
            (0.4, 0.6, "Medium"),
            (0.6, 0.8, "High"),
            (0.8, 1.0, "Very High")
        ]
        
        for min_score, max_score, label in score_ranges:
            count = MessageClassification.objects.filter(
                importance_score__gte=min_score,
                importance_score__lt=max_score if max_score < 1.0 else 1.1
            ).count()
            percentage = (count / total * 100) if total > 0 else 0
            self.stdout.write(f"  {label} ({min_score}-{max_score}): {count} ({percentage:.1f}%)")
        
        # Confidence level stats
        avg_confidence = MessageClassification.objects.aggregate(
            avg_confidence=models.Avg('confidence_level')
        )['avg_confidence'] or 0
        
        self.stdout.write(f"\n🎯 Average confidence level: {avg_confidence:.2f}")
        
        # Top detected keywords
        self.stdout.write(f"\n🔑 Most detected keywords:")
        keyword_counts = {}
        
        for classification in MessageClassification.objects.exclude(detected_keywords=[]):
            for keyword_data in classification.detected_keywords:
                keyword = keyword_data.get('keyword', '')
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Show top 10 keywords
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for keyword, count in sorted_keywords:
            self.stdout.write(f"  '{keyword}': detected {count} times")

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing classifications before creating new ones',
        )
        
        parser.add_argument(
            '--method',
            type=str,
            choices=['keyword', 'ml', 'manual', 'sender_role'],
            help='Force specific classification method for all messages',
        )
        
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.6,
            help='Importance threshold (default: 0.6)',
        )

