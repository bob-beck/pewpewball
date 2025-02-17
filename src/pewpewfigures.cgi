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

####
# 1909 covered figure is 12 inches tall and 12 inches wide
sub figure_1909_covered($$$$$$)
{
    my($gfx, $zx, $zy, $startx, $image_scale, $figure_centred) = @_;
    ## 6 ft 1887 figure.
    my $fy = -2;
    my $fx = -4;
    if ($figure_centred == 1) {
	$fy = -6;
	$fx = -5.25; # hat is 8.5 inches, middle is 5.25 inches in.
    }
    $gfx->move($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line from start to y + 2 inches.
    $fy += 2;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line from here to y + 10, x + 1
    #  which should be upper left corner of top
    #  this should be a curve.
    $fy += 10;
    $fx += 1;
    $gfx->spline($zx + i2ps($fx + 3, $image_scale), $zy + i2ps($fy - 5, $image_scale), $zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line from here to  x + 8.5, 
    $fx += 8.5;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    # line from here to y - 12, x + 5
    # bottom right corner of figure.
    # this should be a curve
    $fy -= 12;
    $fx += 3;
    $gfx->spline($zx + i2ps($fx - 6, $image_scale), $zy + i2ps($fy + 7, $image_scale), $zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
     #  line from here to  x - 12, 
    $fx -= 1;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $gfx->paint();
}    

####
# A 1909 prone figure is 18 inches tall and 21 inches wide
sub figure_1909_prone($$$$$$)
{
    my($gfx, $zx, $zy, $startx, $image_scale,$figure_centred) = @_;
    ## 6 ft 1887 figure.
    my $fy = -3;
    my $fx = -7;
    if ($figure_centred == 1) {
	$fy = -9;
	$fx = -7.25; # hat is 8.5 inches, middle is 7.25 inches in.
    }
    $gfx->move($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line from start to y + 3 inches.
    $fy += 3;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line from here to y + 16, x + 3
    #  which should be upper left corner of top
    #  this should be a curve.
    $fy += 15;
    $fx += 3;
    $gfx->spline($zx + i2ps($fx + 3, $image_scale), $zy + i2ps($fy - 5, $image_scale), $zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line from here to  x + 8.5, 
    $fx += 8.5;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    # line from here to y - 18, x + 11
    # bottom right corner of figure.
    # this should be a curve
    $fy -= 18;
    $fx += 9.5;
    $gfx->spline($zx + i2ps($fx - 12, $image_scale), $zy + i2ps($fy + 9, $image_scale), $zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
     #  line from here to  x - 21, 
    $fx -= 21;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $gfx->paint();
}    

####
# An 1887 figure is 6 feet tall, and 18 inches wide.
# Draw one with the bottom centered at $startx inches
# from the left of the original size target, scaled. 
sub figure_1887($$$$$)
{
    my($gfx, $zx, $zy, $startx, $image_scale,) = @_;
    ## 6 ft 1887 figure.
    my $fy = 0;
    my $fx = $startx;
    $gfx->move($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line from start to x - 6 inches.
    $fx -= 6;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to y + 30 inches
    $fy += 30;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x - 6 inches, y + 12 inches
    $fx -= 6;
    $fy += 12;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to y + 18 inches
    $fy += 18;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x + 6 inches
    $fx += 6;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to y + 6 inches
    $fy += 6;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x + 6 inches, y + 6 inches
    $fx += 6;
    $fy += 6;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  lint to x + 6 inches, y - 6 inches
    $fx += 6;
    $fy -= 6;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to y - 6 inches
    $fy -= 6;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x + 6 inches
    $fx += 6;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to y - 18 inches
    $fy -= 18;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  lint to x - 6 inches, y - 12 inches
    $fx -= 6;
    $fy -= 12;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to y - 30 inches
    $fy -= 30;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x - 6 inches (at start)
    $fx -= 6;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $gfx->paint();
}

sub make1855Target($$$$$) {
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

    my $real_width = 24 * 72;
    my $real_height = 72 * 72;
    my $real_bull_radius = 4 * 72;
    my $real_magpie_radius = 12 * 72;
    my $real_magpie_thickness = 0.75 * 72;

    my ($scale_width, $scale_height) =
	scaled_dimensions($x2 - $x1, $y2 - $y1, $real_width, $real_height);
    my $image_scale = $scale_height / $real_height;
    if ($centre) {
	# scale only centre of target
	($scale_width, $scale_height) =
	    scaled_dimensions($x2 - $x1, $y2 - $y1, $real_magpie_radius * 2, $real_magpie_radius * 2);
	$image_scale = $scale_height / ($real_magpie_radius * 2);
    }

    my $width_inches = round($scale_width / 72, 1);
    my $height_inches = round($scale_height / 72, 1);

    my $delta_h = ($y2 - $y1 - $scale_height) / 2;
    my $delta_w = ($x2 - $x1 - $scale_width) / 2;

    # Find the centre of the page.
    my $midx = ($x2 - $x1) / 2 + $x1;
    my $midy = ($y2 - $y1) / 2 + $y1;

    # Put text on target
    $txt -> fillcolor("grey");
    $txt -> strokecolor("grey");
    $txt->font($pdf->corefont('Helvetica Bold'), 10);
    $txt->position($trim ?  $x1 + 10 : $x1 + 30, $trim ? $y2 - 10 : $y2 - 30);

    my $tinch = "24 X 72";

    $txt->text ("pewpewball.com 1855 musketry target, $width_inches X $height_inches inches, original $tinch.");
    $txt->font($pdf->corefont('Helvetica'), 10);
    $txt->crlf();
    if ($centre == 1) {
	my $backing_width = round(($real_width * $image_scale) / 72, 2);
	my $backing_height = round(($real_height * $image_scale) / 72, 2);
        $txt->text ("This target centre should be in the centre of a $backing_width X $backing_height inch white scoring outer paper");
	$txt->crlf();
    }
    $txt->font($pdf->corefont('Helvetica'), 8);
    shootat($txt, 100, $image_scale);
    shootat($txt, 200, $image_scale);
    shootat($txt, 300, $image_scale);
    shootat($txt, 500, $image_scale);
    shootat($txt, 900, $image_scale);

    # Draw bull and magpie we use a grey ring to be
    # visible on both the black and white portions
    # of the target
    $gfx -> strokecolor("black");
    $gfx -> fillcolor("black");

    my $magpie_radius = $real_magpie_radius * $image_scale;
    $gfx -> circle( $midx, $midy, $magpie_radius);
    $gfx -> paint();

    $gfx -> strokecolor("white");
    $gfx -> fillcolor("white");
    $magpie_radius = ($real_magpie_radius - $real_magpie_thickness) * $image_scale;
    $gfx -> circle( $midx, $midy, $magpie_radius);
    $gfx -> paint();

    $gfx -> strokecolor("black");
    $gfx -> fillcolor("black");
    
    my $bull_radius = $real_bull_radius * $image_scale;
    $gfx -> circle( $midx, $midy, $bull_radius);
    $gfx -> paint();

    if ($centre == 0) { 
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
    }

    return $pdf->to_string();
    $pdf -> end;
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

    my $real_width = 48 * 72;
    my $real_height = 72 * 72;
    if ($class == 2) {
	$real_width = 72 * 72;
	$real_height = 72 * 72;
    }
    if ($class == 1) {
	$real_width = 96 * 72;
	$real_height = 72 * 72;
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


    # Draw our figures on the target in the correct locations. 
    $gfx -> strokecolor("black");
    if ($class == 3) {
	figure_1887($gfx, $x1 + $delta_w, $y1 + $delta_h, 24, $image_scale);
    }
    if ($class == 2) {
	figure_1887($gfx, $x1 + $delta_w, $y1 + $delta_h, 12, $image_scale);
	figure_1887($gfx, $x1 + $delta_w, $y1 + $delta_h, 36, $image_scale);
	figure_1887($gfx, $x1 + $delta_w, $y1 + $delta_h, 60, $image_scale);
    }
    if ($class == 1) {
	figure_1887($gfx, $x1 + $delta_w, $y1 + $delta_h, 12, $image_scale);
	figure_1887($gfx, $x1 + $delta_w, $y1 + $delta_h, 36, $image_scale);
	figure_1887($gfx, $x1 + $delta_w, $y1 + $delta_h, 60, $image_scale);
	figure_1887($gfx, $x1 + $delta_w, $y1 + $delta_h, 84, $image_scale);
    }
    
    # Put text on target, we use grey to be visible in both the black and
    # white portions of the target.
    $txt -> fillcolor("grey");
    $txt -> strokecolor("grey");
    $txt->font($pdf->corefont('Helvetica Bold'), 10);
    $txt->position($trim ?  $x1 + 10 : $x1 + 30, $trim ? $y2 - 10 : $y2 - 30);

    my $tclass = "third";
    my $tinch = "48 X 72";
    if ($class == 2) {
	$tclass = "second";
	$tinch = "72 X 72";
    }
    if ($class == 1) {
	$tclass = "first";
	$tinch = "96 X 72";
    }
    $txt->text ("pewpewball.com 1887 $tclass class musketry target, $width_inches X $height_inches inches, original $tinch.");
    $txt->font($pdf->corefont('Helvetica'), 10);
    $txt->crlf();
    if ($class == 3 || $class == 2) {
	shootat($txt, 200, $image_scale);
	shootat($txt, 300, $image_scale);
    }
    if ($class == 2) {
	shootat($txt, 400, $image_scale);
    }
    if ($class == 1) {
	shootat($txt, 500, $image_scale);
	shootat($txt, 600, $image_scale);
	shootat($txt, 700, $image_scale);
	shootat($txt, 800, $image_scale);
    }

    # Draw bull and magpie we use a grey ring to be
    # visible on both the black and white portions
    # of the target
    $gfx -> strokecolor("grey");

    my $real_bull_radius = 6 * 72;
    my $real_magpie_radius = 18 * 72;
    if ($class == 2) {
	$real_bull_radius = 12 * 72;
	$real_magpie_radius = 24 * 72;
    } 
    if ($class == 1) {
	$real_bull_radius = 18 * 72;
	$real_magpie_radius = 30 * 72;
    } 

    my $magpie_radius = $real_magpie_radius * $image_scale;
    $gfx -> circle( $midx, $midy, $magpie_radius);
    $gfx -> stroke();

    my $bull_radius = $real_bull_radius * $image_scale;
    $gfx -> circle( $midx, $midy, $bull_radius);
    $gfx -> stroke();

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

sub make1891Target($$$$$) {
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

    my $real_width = 48 * 72;
    my $real_height = 48 * 72;
    if ($class == 2) {
	$real_width = 72 * 72;
	$real_height = 72 * 72;
    }
    if ($class == 1) {
	$real_width = 96 * 72;
	$real_height = 72 * 72;
    }
    my $real_bull_radius = 6 * 72;
    my $real_magpie_radius = 12 * 72;
    if ($class == 2) {
	$real_bull_radius = 12 * 72;
	$real_magpie_radius = 24 * 72;
    } 
    if ($class == 1) {
	$real_bull_radius = 18 * 72;
	$real_magpie_radius = 30 * 72;
    } 

    my ($scale_width, $scale_height) =
	scaled_dimensions($x2 - $x1, $y2 - $y1, $real_width, $real_height);
    my $image_scale = $scale_height / $real_height;
    if ($centre) {
	# scale only centre of target
	($scale_width, $scale_height) =
	    scaled_dimensions($x2 - $x1, $y2 - $y1, $real_magpie_radius * 2, $real_magpie_radius * 2);
	$image_scale = $scale_height / ($real_magpie_radius * 2);
    }

    my $width_inches = round($scale_width / 72, 1);
    my $height_inches = round($scale_height / 72, 1);

    my $delta_h = ($y2 - $y1 - $scale_height) / 2;
    my $delta_w = ($x2 - $x1 - $scale_width) / 2;

    # Find the centre of the page.
    my $midx = ($x2 - $x1) / 2 + $x1;
    my $midy = ($y2 - $y1) / 2 + $y1;

    # Put text on target
    $txt -> fillcolor("grey");
    $txt -> strokecolor("grey");
    $txt->font($pdf->corefont('Helvetica Bold'), 10);
    $txt->position($trim ?  $x1 + 10 : $x1 + 30, $trim ? $y2 - 10 : $y2 - 30);

    my $tclass = "third";
    my $tinch = "48 X 48";
    if ($class == 2) {
	$tclass = "second";
	$tinch = "72 X 72";
    }
    if ($class == 1) {
	$tclass = "first";
	$tinch = "96 X 72";
    }
    $txt->text ("pewpewball.com 1891-1902 $tclass class musketry target, $width_inches X $height_inches inches, original $tinch.");
    $txt->font($pdf->corefont('Helvetica'), 10);
    $txt->crlf();
    if ($centre == 1) {
	my $backing_width = round(($real_width * $image_scale) / 72, 2);
	my $backing_height = round(($real_height * $image_scale) / 72, 2);
        $txt->text ("This target centre should be in the centre of a $backing_width X $backing_height inch white scoring outer paper");
	$txt->crlf();
    }
    if ($class == 3 || $class == 2) {
	shootat($txt, 200, $image_scale);
	shootat($txt, 300, $image_scale);
    }
    if ($class == 2) {
	shootat($txt, 400, $image_scale);
    }
    if ($class == 1) {
	shootat($txt, 500, $image_scale);
	shootat($txt, 600, $image_scale);
	shootat($txt, 700, $image_scale);
	shootat($txt, 800, $image_scale);
    }

    # Draw bull and magpie we use a grey ring to be
    # visible on both the black and white portions
    # of the target
    $gfx -> strokecolor("black");
    $gfx -> fillcolor("black");

    my $magpie_radius = $real_magpie_radius * $image_scale;
    $gfx -> circle( $midx, $midy, $magpie_radius);
    $gfx -> stroke();

    my $bull_radius = $real_bull_radius * $image_scale;
    $gfx -> circle( $midx, $midy, $bull_radius);
    $gfx -> paint();

    if ($centre == 0) { 
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
    }

    return $pdf->to_string();
    $pdf -> end;
}

sub make1909Target($$$$$$) {
    my($paper, $class, $topcolour, $bottomcolour, $trim, $figure_centred) = @_;

    my @colours = ("black", "white", "red", "lime", "fuchsia", "orange", "blue", "green",
		   "navy", "yellow", "olive", "gray", "brown", "tan", "bronze");

    my @papers= ("A0", "A1", "A2", "A3", "A4", "Letter", "Legal", "11x17", "12x18", "24x36", "36x36", "36x48", "48x48", "72x72");

    die "Paper $paper is not valid"
	unless (grep(/^$paper$/, @papers));

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
    $page->boundaries(media => $paper);
    $page->boundaries(media => $paper, trim => $trim * 72);
    my ($x1, $y1, $x2, $y2) = $page->boundaries('media');

    ($x1, $y1, $x2, $y2) = $page->boundaries('trim');

    # A 1909 target has the properties that the magpie is 2/3 the size of the paper dimension,
    # and the bull is 1/2 this size of the paper dimension, assuming the paper is square.

    
    my $gfx  = $page -> graphics();
    my $txt  = $page -> text;

    my $real_width = 48 * 72;
    my $real_height = 48 * 72;
    if ($class == 1) {
	$real_width = 72 * 72;
	$real_height = 72 * 72;
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


    $gfx -> fillcolor($bottomcolour);
    $gfx -> strokecolor($bottomcolour);
    $gfx -> rectangle($x1 + $delta_w, $y1 + $delta_h, $x2 - $delta_w, $midy);
    $gfx ->fill;
    $gfx -> fillcolor($topcolour);
    $gfx -> strokecolor($topcolour);
    $gfx -> rectangle($x1 + $delta_w, $midy, $x2 - $delta_w, $y2 - $delta_h);
    $gfx ->fill;

    $txt -> fillcolor("black");
    $txt -> strokecolor("black");
    if ($topcolour eq "black" || $bottomcolour eq "black") {
	$txt -> strokecolor("#654321");
	$txt -> fillcolor("#654321");
    }

    # Finally, put some text on the target
    $txt->font($pdf->corefont('Helvetica Bold'), 14);
    $txt->position($x1 + 30, $y2 - 30);

    my $tclass = "second";
    my $tinch = "48 X 48";
    if ($class == 1) {
	$tclass = "first";
	$tinch = "72 X 72";
    }
    $txt->text ("pewpewball.com 1909 $tclass class musketry target, $width_inches X $height_inches inches, original $tinch.");
    $txt->font($pdf->corefont('Helvetica'), 10);
    $txt->crlf();
    if ($class == 3 || $class == 2) {
	shootat($txt, 200, $image_scale);
	shootat($txt, 300, $image_scale);
	shootat($txt, 400, $image_scale);
    }
    if ($class == 1) {
	shootat($txt, 500, $image_scale);
	shootat($txt, 600, $image_scale);
	shootat($txt, 700, $image_scale);
	shootat($txt, 800, $image_scale);
    }

    # Put the correct figure on the target, in a hopefully something
    # like convincing khaki of the time colour as opposed to whatever
    # the fashionistas doing colour palettes call "khaki" today.
    # It does need to be visible in any of our allowed backgrounds.
    $gfx -> strokecolor("#654321");
    $gfx -> fillcolor("#654321");
    if ($class == 1) {
	figure_1909_prone($gfx, $midx, $midy, 24, $image_scale, $figure_centred);
    } else {
	figure_1909_covered($gfx, $midx, $midy, 24, $image_scale, $figure_centred);
    }

    # Draw the magpie and bull rings.
    $gfx -> strokecolor("black");
    $gfx -> fillcolor("black");
    if ($topcolour eq "black" || $bottomcolour eq "black") {
	$gfx -> strokecolor("#654321");
	$gfx -> fillcolor("#654321");
    }

    my $real_bull_radius = 12;
    my $real_magpie_radius = 18;
    if ($class == 1) {
	$real_bull_radius = 20;
	$real_magpie_radius = 28;
    } 

    my $magpie_radius = i2ps($real_magpie_radius, $image_scale);
    $gfx -> circle( $midx, $midy, $magpie_radius);
    $gfx -> stroke();

    my $bull_radius = i2ps($real_bull_radius, $image_scale);
    $gfx -> circle( $midx, $midy, $bull_radius);
    $gfx -> stroke();

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
my $FigureCentred = $cgi->param('FigureCentred');

my $Top = $cgi->param('Top'); 
my $Bottom = $cgi->param('Bottom'); 

my $Centre = $cgi->param('Centre'); 

my $pdfstring;
if ($Year == 1855) {
    $pdfstring = make1855Target($Paper, $Class, $Orientation, $Trim, $Centre);
}
if ($Year == 1887) {
    $pdfstring = make1887Target($Paper, $Class, $Orientation, $Trim);
}
if ($Year == 1891) {
    $pdfstring = make1891Target($Paper, $Class, $Orientation, $Trim, $Centre);
}
if ($Year == 1909) {
    $pdfstring = make1909Target($Paper, $Class, $Top, $Bottom, $Trim, $FigureCentred);
}
print $cgi->header('application/pdf');
print $pdfstring;
