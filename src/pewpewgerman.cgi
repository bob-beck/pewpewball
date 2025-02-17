#!/usr/bin/perl
# Copyright (c) 2025 Bob Beck <beck@obtuse.com>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

use warnings;
use strict;

use PDF::API2;
use CGI ':standard';

####
# Helpful constants.

# PDF natively uses a point size of 72 per inch, so all coordinates are
# done based on that.
use constant mm => 25.4 / 72;
use constant inches => 1 / 72;
use constant YardsPerMetre => 0.9144;

# These were translated to English and turned into 2 decimal places of
# inches.  Anything to avoid metric.. sheesh.
use constant BandTargetHeight => 1700 / mm;
use constant BandTargetWidth => 1200 / mm;
use constant BandWidth => 60 / mm;
use constant BandHitWidth => 120 / mm;
use constant ManBreadthWidth => 400 / mm;
use constant RingCircleRadius => 50 / mm;
use constant CrossPatchWidth => 200 / mm;
use constant CrossPatchHeight => 100 / mm;

#####
# Round a number.
sub round($$)
{
  my ($value, $places) = @_;
  my $factor = 10**$places;
  return int($value * $factor + 0.5) / $factor;
}

####
# Take page width, page height, target width, targe height
# Return scaled dimensions to fit inside the page preserving
# the original aspect ratio. 
sub scaled_dimensions($$$$) {
    my($pw, $ph, $tw, $th) = @_;
    my $rt = $tw / $th; # aspect ratio of target
    my $rp = $pw / $ph; # aspect ratio of page
    if ($rp > $rt) {
	return ($tw * $ph / $th, $ph);
    } else {
	return ($pw,  $th *  $pw / $tw);
    }
}

####
# Return points, scaled
sub ps($$)
{
    my($points, $scale) = @_;
    return round($points * $scale, 0);
}

####
# Print equivalent shooting distance to original in yards.
sub shootat($$$) {
    my ($txt, $distance, $scale) = @_;
    my $metres = round($distance * $scale, 0);
    my $yards = round($metres / YardsPerMetre, 0);
    $txt->text("Shooting at $metres M ($yards Yds) is equivalent to original at $distance M");
    $txt->crlf();
}

####
sub german_1887_band($$$$$$)
{
    my($gfx, $x1, $y1, $x2, $y2, $image_scale) = @_;
    my $midx = ($x2 - $x1) / 2 + $x1;
    my $midy = ($y2 - $y1) / 2 + $y1;

    $gfx -> fillcolor("black");
    $gfx -> strokecolor("black");
    #  Make a rectancle from top to bottom the diameter of the bull.
    $gfx -> rectangle($midx - ps(BandWidth / 2, $image_scale), $y1, $midx + ps(BandWidth / 2, $image_scale), $y2);
    $gfx->paint();
    # Make a cross patch 250 mm above and below the midpoint
    $gfx -> rectangle($midx - ps(CrossPatchWidth / 2, $image_scale),
		      $midy + ps(5 * RingCircleRadius, $image_scale),
		      $midx + ps(CrossPatchWidth / 2, $image_scale),
		      $midy + ps((5 * RingCircleRadius) + CrossPatchHeight, $image_scale));
    $gfx->paint();
    $gfx -> rectangle($midx - ps(CrossPatchWidth / 2, $image_scale),
		      $midy - ps(5 * RingCircleRadius, $image_scale),
		      $midx + ps(CrossPatchWidth / 2, $image_scale),
		      $midy - ps((5 * RingCircleRadius) + CrossPatchHeight, $image_scale));
    $gfx->paint();
    $gfx -> circle($midx, $midy, ps(3 * RingCircleRadius, $image_scale));
    $gfx -> paint();
    $gfx -> fillcolor("white");
    $gfx -> strokecolor("white");
    $gfx -> circle($midx, $midy, ps(RingCircleRadius, $image_scale));
    $gfx -> paint();
    $gfx -> fillcolor("black");
    $gfx -> strokecolor("black");
}

sub german_1887_rings($$$$$$)
{
    my($gfx, $x1, $y1, $x2, $y2, $image_scale) = @_;
    my $midx = ($x2 - $x1) / 2 + $x1;
    my $midy = ($y2 - $y1) / 2 + $y1;

    $gfx -> fillcolor("grey");
    $gfx -> strokecolor("grey");
    $gfx -> circle($midx, $midy, ps(2 * RingCircleRadius, $image_scale));
    $gfx -> stroke();
    $gfx -> fillcolor("black");
    $gfx -> strokecolor("black");
    for (my $i = 3; $i < 13; $i++) {
	$gfx -> circle($midx, $midy, ps($i*RingCircleRadius, $image_scale));
	$gfx -> stroke();
    }
}

sub make1887Target($$$$) {
    my($paper, $class, $orientation, $trim) = @_;

    my $pdf  = PDF::API2->new;

    # Try to prevent scaling in viewers which may turn into scaling when
    # printed from viewers (i.e. a browser) instead of sending the file
    # directly to a printer.
    $pdf->preferences(-printscalingnone=>1);

    # Set our page boundaries to the correct paper size, with repeated
    # hints to attempt to ensure the randomly written browser and
    # printer software stacks that will be touching this will
    # hopefully be convinced to not pervert it themselves. We probably
    # can't win 100% of the time, but it would be nice if it is usually
    # correct in the common cases with the correct paper size selected.
    $pdf->mediabox($paper);
    my $page = $pdf  -> page;
    $page->boundaries(media => $paper, trim => $trim * 72);
    my ($x1, $y1, $x2, $y2) = $page->boundaries('media');

    if ($orientation eq "Landscape") {
	# make it landscape
	$pdf->mediabox($y1, $x1, $y2, $x2);
	$page->boundaries(media => [$y1, $x1, $y2, $x2], trim => $trim * 72);
    }
    ($x1, $y1, $x2, $y2) = $page->boundaries('trim');

    my $gfx  = $page -> graphics();
    my $txt  = $page -> text;

    my ($scale_width, $scale_height) =
	scaled_dimensions($x2 - $x1, $y2 - $y1, BandTargetWidth, BandTargetHeight);

    my $image_scale = $scale_height / BandTargetHeight;

    my $width_mm = round($scale_width * mm, 0);
    my $height_mm = round($scale_height * mm, 0);

    my $delta_h = ($y2 - $y1 - $scale_height) / 2;
    my $delta_w = ($x2 - $x1 - $scale_width) / 2;

    # Find the centre of the page.
    my $midx = ($x2 - $x1) / 2 + $x1;
    my $midy = ($y2 - $y1) / 2 + $y1;

    # Put text on target
    $txt -> fillcolor("black");
    $txt -> strokecolor("black");
    $txt->font($pdf->corefont('Helvetica Bold'), 10);
    $txt->position($trim ?  $x1 + 10 : $x1 + 30, $trim ? $y2 - 10 : $y2 - 30);

    $txt->text ("pewpewball.com 1887 German musketry target");
    $txt->crlf();
    $txt->text ("$width_mm X $height_mm mm, original 1200 x 1700 mm");
    $txt->crlf();
    $txt->font($pdf->corefont('Helvetica'), 10);
    $txt->font($pdf->corefont('Helvetica'), 8);
    shootat($txt, 100, $image_scale);
    shootat($txt, 200, $image_scale);
    shootat($txt, 300, $image_scale);
    shootat($txt, 400, $image_scale);
    shootat($txt, 600, $image_scale);


    # Draw our figures on the target in the correct locations. 
    $gfx -> strokecolor("black");
    german_1887_band($gfx, $x1 + $delta_w , $y1 + $delta_h, $x2 - $delta_w,
		     $y2 - $delta_h,  $image_scale);
    if ($class == 2) {
	# make the brown rectangles on either side
	$gfx -> strokecolor("tan");
	$gfx -> fillcolor("tan");
	$gfx -> rectangle($x1 + $delta_w, $y1 + $delta_h,
			  $x1 + $delta_w + ps(ManBreadthWidth, $image_scale),
			  $y2 - $delta_h);
	$gfx -> paint();
	$gfx -> rectangle($x2 - $delta_w, $y1 + $delta_h,
			  $x2 - $delta_w - ps(ManBreadthWidth, $image_scale),
			  $y2 - $delta_h);
	$gfx -> paint();
	german_1887_rings($gfx, $x1, $y1, $x2, $y2,  $image_scale);
    } else {
	# Draw red lines for band hits
	$gfx -> strokecolor("red");
	$gfx->move($midx - ps(BandHitWidth / 2, $image_scale), $y1 + $delta_h);
	$gfx->line($midx - ps(BandHitWidth / 2, $image_scale), $y2 - $delta_h);
	$gfx->stroke();
	$gfx->move($midx + ps(BandHitWidth / 2, $image_scale), $y1 + $delta_h);
	$gfx->line($midx + ps(BandHitWidth / 2, $image_scale), $y2 - $delta_h);
	$gfx->stroke();
	$gfx -> strokecolor("black");
	# Draw blacklines for Man Breadth
	$gfx->move($midx - ps(ManBreadthWidth / 2, $image_scale), $y1 + $delta_h);
	$gfx->line($midx - ps(ManBreadthWidth / 2, $image_scale), $y2 - $delta_h);
	$gfx->stroke();
	$gfx->move($midx + ps(ManBreadthWidth / 2, $image_scale), $y1 + $delta_h);
	$gfx->line($midx + ps(ManBreadthWidth / 2, $image_scale), $y2 - $delta_h);
	$gfx->stroke();
    }
    # Draw lines for outer target boundary, if needed when the paper is taller
    # or wider than the correct target boundary maintaining the correct scale.
    if ($delta_h != 0) {
	$gfx->move($x1, $y1 + $delta_h);
	$gfx->line($x2, $y1 + $delta_h);
	$gfx->stroke();
	$gfx->move($x1, $y2 - $delta_h);
	$gfx->line($x2, $y2 - $delta_h);
	$gfx->stroke();
    }
    if ($delta_w != 0) {
	$gfx->move($x1 + $delta_w, $y1);
	$gfx->line($x1 + $delta_w, $y2);
	$gfx->stroke();
	$gfx->move($x2 - $delta_w, $y1);
	$gfx->line($x2 - $delta_w, $y2);
	$gfx->stroke();
    }

    return $pdf->to_string();
    $pdf -> end;
}

####
# Main program, just do the CGI thing

my $cgi = CGI->new();
my $Year = $cgi->param('Year');
my $Paper = $cgi->param('Paper');
my $Class = $cgi->param('Class');
my $Orientation = $cgi->param('Orientation');
my $Trim = $cgi->param('Trim');

my $Top = $cgi->param('Top'); 
my $Bottom = $cgi->param('Bottom'); 

my $Centre = $cgi->param('Centre'); 

my $pdfstring;
if ($Year == 1887) {
    $pdfstring = make1887Target($Paper, $Class, $Orientation, $Trim);
}
print $cgi->header('application/pdf');
print $pdfstring;
