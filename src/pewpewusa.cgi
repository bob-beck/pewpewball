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
use constant YardsPerMetre => 0.9144;

# 1889 USA targets A B and C - From Stanhorpe Blunt's Manual
# These were eliipses so we keep a major / minor axis size
use constant A_Width => 48 * 72;
use constant A_Height => 72 * 72;
use constant A_Bull_Minor => 4 * 72;
use constant A_Bull_Major => 5 * 72;
use constant A_Inner_Minor => 12 * 72;
use constant A_Inner_Major => 15 * 72;
use constant A_Outer_Minor => 20 * 72;
use constant A_Outer_Major => 29.5 * 72;

use constant B_Width => 72 * 72;
use constant B_Height => 72 * 72;
use constant B_Bull_Minor => 9 * 72;
use constant B_Bull_Major => 12* 72;
use constant B_Inner_Minor => 18 * 72;
use constant B_Inner_Major => 24 * 72;
use constant B_Outer_Minor => 27 * 72;
use constant B_Outer_Major => 36 * 72;

use constant C_Width => 144 * 72;
use constant C_Height => 72 * 72;
use constant C_Bull_Minor => 16 * 72;
use constant C_Bull_Major => 22.5* 72;
use constant C_Inner_Minor => 25.5 * 72;
use constant C_Inner_Major => 36 * 72;
# outer is vertical straight line at 6 ft width

use constant VeryLightBuff => "#f9f1cf";  # very light buff?
use constant LineWidth => 72/4;  # 1/4 inch line width.

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
# Return inches to points, scaled
sub i2ps($$)
{
    my($inch, $scale) = @_;
    return round($inch * 72 * $scale, 0);
}

####
# Print equivalent shooting distance to original in yards.
sub shootat($$$) {
    my ($txt, $distance, $scale) = @_;
    my $yards = round($distance * $scale, 0);
    my $metres = round($yards * YardsPerMetre, 0);
    $txt->text("Shooting at $yards Yards ($metres Metres) is equivalent to original at $distance Yards");
    $txt->crlf();
}

sub makeUSA1889centre($$$$$$$$$$$$$) {
    my ($gfx, $target_background, $x1, $y1, $x2, $y2, $bx, $by, $ix, $iy,
	$ox, $oy, $image_scale) = @_;

    # Find the centre of the page.
    my $midx = ($x2 - $x1) / 2 + $x1;
    my $midy = ($y2 - $y1) / 2 + $y1;

    # make the outer ellipse
    if ($ox > 0 && $oy > 0) {
	$gfx -> strokecolor("black");
	$gfx -> fillcolor("black");
	$gfx -> ellipse($midx, $midy, ($ox) * $image_scale, ($oy) * $image_scale);
	$gfx -> paint();
	$gfx -> strokecolor($target_background);
	$gfx -> fillcolor($target_background);
	$gfx -> ellipse($midx, $midy, ($ox - LineWidth) * $image_scale,
			($oy - LineWidth) * $image_scale);
	$gfx -> paint();
	$gfx -> strokecolor("black");
	$gfx -> fillcolor("black");
    }

    # make inner ellipse
    if ($ix > 0 && $iy > 0) {
	$gfx -> strokecolor("black");
	$gfx -> fillcolor("black");
	$gfx -> ellipse($midx, $midy, ($ix) * $image_scale, ($iy) * $image_scale);
	$gfx -> paint();
	$gfx -> strokecolor($target_background);
	$gfx -> fillcolor($target_background);
	$gfx -> ellipse($midx, $midy, ($ix - LineWidth) * $image_scale,
			($iy - LineWidth) * $image_scale);
	$gfx -> paint();
	$gfx -> strokecolor("black");
	$gfx -> fillcolor("black");
    }
    # make the bull ellipse.
    if ($bx > 0 && $by > 0) {
	$gfx -> ellipse($midx, $midy, $bx * $image_scale, $by * $image_scale);
	$gfx -> paint();
    }
}

sub make1889Target($$$$$) {
    my($paper, $class, $orientation, $trim, $centre) = @_;

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

    my $real_width = A_Width;
    my $real_height = A_Height;
    if ($class == 2) {
	$real_width = B_Width;
	$real_height = B_Height;
    }
    if ($class == 1) {
	$real_width = C_Width;
	$real_height = C_Height;
    }
    if ($class == 0) {
	# Target C inner only. 
	$real_width = B_Width;
	$real_height = B_Height;
    }
	
    my ($scale_width, $scale_height) =
	scaled_dimensions($x2 - $x1, $y2 - $y1, $real_width, $real_height);
    my $image_scale = $scale_height / $real_height;

    my $width_inches = round($scale_width / 72, 1);
    my $height_inches = round($scale_height / 72, 1);

    my $delta_h = ($y2 - $y1 - $scale_height) / 2;
    my $delta_w = ($x2 - $x1 - $scale_width) / 2;

    # Find the centre of the page.
    my $midx = ($x2 - $x1) / 2 + $x1;
    my $midy = ($y2 - $y1) / 2 + $y1;

    my $target_background = VeryLightBuff;

    $gfx -> fillcolor($target_background); # very light buff?
    $gfx -> strokecolor($target_background); # very light buff?);
    $gfx -> rectangle($x1 + $delta_w, $y1 + $delta_h, $x2 - $delta_w, $y2 - $delta_h);
    $gfx ->fill;
    
    # Put text on target
    $txt -> fillcolor("grey");
    $txt -> strokecolor("grey");
    $txt->font($pdf->corefont('Helvetica Bold'), 10);
    $txt->position($trim ?  $x1 + 10 : $x1 + 30, $trim ? $y2 - 10 : $y2 - 30);
    

    my $tinch = "48 X 72";
    my $tname = "A";
    if ($class == 2) {
        $tinch = "72 X 72";
        $tname = "B";
    }
    if ($class == 1) {
	$tinch = "144 X 72";
        $tname = "C";
    }
    if ($class == 0) {
	$tinch = "72 X 72";
        $tname = "C inner";
    }

    $txt->font($pdf->corefont('Helvetica'), 10);
    $txt->text ("pewpewball.com 1889 USA target $tname, $width_inches X $height_inches inches, original $tinch.");
    $txt->font($pdf->corefont('Helvetica'), 10);
    $txt->crlf();
    if ($centre == 1) {
	my $backing_width = round(($real_width * $image_scale) / 72, 2);
	my $backing_height = round(($real_height * $image_scale) / 72, 2);
        $txt->text ("This target centre should be in the centre of a $backing_width X $backing_height inch white scoring outer paper");
	$txt->crlf();
    }
    $txt->font($pdf->corefont('Helvetica'), 8);

    if ($class == 3) {
	shootat($txt, 100, $image_scale);
	shootat($txt, 200, $image_scale);
	shootat($txt, 300, $image_scale);
	makeUSA1889centre($gfx, $target_background, $x1 + $delta_w, $y1 + $delta_h,
			  $x2 - $delta_w, $y2 - $delta_h,
			   A_Bull_Minor, A_Bull_Major,
			   A_Inner_Minor, A_Inner_Major,
			   A_Outer_Minor, A_Outer_Major,
			   $image_scale);
	
    }
    if ($class == 2) {
	shootat($txt, 400, $image_scale);
	shootat($txt, 500, $image_scale);
	shootat($txt, 600, $image_scale);
	makeUSA1889centre($gfx, $target_background, $x1 + $delta_w, $y1 + $delta_h,
			  $x2 - $delta_w, $y2 - $delta_h,
			   B_Bull_Minor, B_Bull_Major,
			   B_Inner_Minor, B_Inner_Major,
			   B_Outer_Minor, B_Outer_Major,
			   $image_scale);
    }
    if ($class == 1 || $class == 0) {
	shootat($txt, 700, $image_scale);
	shootat($txt, 800, $image_scale);
	shootat($txt, 900, $image_scale);
	$gfx -> fillcolor("black");
	$gfx -> strokecolor("black");
	# draw the lines for the outer area.
	my $left_offset = $scale_width / 4;
	my $right_offset = $scale_width * 3 / 4;
	if ($class == 0) {
	    $left_offset = 0;
	    $right_offset = 0;
	}
	$gfx->rectangle($x1 + $delta_w + $left_offset,
			$y1 + $delta_h,
			$x1 + $delta_w + $left_offset + (LineWidth * $image_scale),
			$y2 - $delta_h);
	$gfx->paint();
	$gfx->rectangle($x1 + $delta_w + $right_offset - (LineWidth * $image_scale),
			$y1 + $delta_h,
			$x1 + $delta_w + $right_offset,
			$y2 - $delta_h);
	makeUSA1889centre($gfx, $target_background, $x1 + $delta_w, $y1 + $delta_h,
			  $x2 - $delta_w, $y2 - $delta_h,
			   C_Bull_Minor, C_Bull_Major,
			   C_Inner_Minor, C_Inner_Major,
			   0, 0,
			  $image_scale);
    }

    if ($centre == 0) { 
	# Draw lines for outer target boundary, if needed when the paper is taller
	# or wider than the correct target boundary maintaining the correct scale.
	$gfx -> fillcolor("black");
	$gfx -> strokecolor("black");
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
if ($Year == 1889) {
    $pdfstring = make1889Target($Paper, $Class, $Orientation, $Trim, $Centre);
}
print $cgi->header('application/pdf');
print $pdfstring;
