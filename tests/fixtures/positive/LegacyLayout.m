#import <UIKit/UIKit.h>

@implementation LegacyLayoutController

- (void)viewDidLayoutSubviews {
    [super viewDidLayoutSubviews];

    CGFloat scale = [UIScreen mainScreen].scale;
    BOOL landscape = UIInterfaceOrientationIsLandscape(self.interfaceOrientation);
    self.view.frame = CGRectMake(
        0,
        0,
        390,
        844
    );
    [self.view setCenter:CGPointMake(
        CGRectGetMidX(self.view.bounds),
        CGRectGetMidY(self.view.bounds)
    )];
    UIToolbar *toolbar = [[UIToolbar alloc] initWithFrame:CGRectZero];
    self.insetsLayoutMarginsFromSafeArea = NO;
    (void)scale;
    (void)landscape;
    (void)toolbar;
}

@end
