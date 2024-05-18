class Review:
    def __init__(
        self,
        reviewer_name,
        review_profile,
        review_title,
        review_stars,
        review_date,
        traveler_types,
        review_text,
        review_writing_date,
    ):
        self.reviewer_name = reviewer_name
        self.review_profile = review_profile
        self.review_title = review_title
        self.review_stars = review_stars
        self.review_date = review_date
        self.traveler_types = traveler_types
        self.review_text = review_text
        self.review_writing_date = review_writing_date

    def __str__(self):
        return f"Name: {self.reviewer_name}\nProfile: {self.review_profile}\nTitle: {self.review_title}\nStars: {self.review_stars}\nDate: {self.review_date}\nTraveler Types: {self.traveler_types}\nReview: {self.review_text} \nWriting Date: {self.review_writing_date}\n\n"

    def to_csv(self):
        return [
            self.reviewer_name,
            self.review_profile,
            self.review_title,
            self.review_stars,
            self.review_date,
            self.traveler_types,
            self.review_text,
            self.review_writing_date,
        ]
