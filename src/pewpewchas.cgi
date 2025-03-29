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
use constant scale_base => 3 / 4;

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
    my $metres = round($distance * $scale, 0);
    my $yards = round($metres / YardsPerMetre, 0);
    $txt->text("Shooting at $metres M ($yards Yds) is equivalent to centrefire target at $distance M");
    $txt->crlf();
}


####
# An CHAS service target is 22 inches wide and 30 inches tall printed on 24x36 paper.
# which is the 1.5 scale version of the official target shot at 300 and 200 meters
# which should be printed on 18x24 paper. The "official" centrefire normal target
# becomes this figure printed at scale_base scale.
#
# Draw one with the bottom centered at $startx inches
# from the left of the original size target, scaled. 
sub figure_chas($$$$$$)
{
    my($gfx, $page, $pdf,  $zx, $zy, $image_scale,) = @_;

    # Since this was originally designed for a 24x36 page, but we
    # actually want scale 1 to be at 18x24, We modify the provided
    # image scale so when we ask for an image scale of 1.0, we get an
    # image scale of 0.667 to match what we want the "official" size
    # target to be.  (It's either that or I manually change all the
    # consttants)
    $image_scale = $image_scale * scale_base;

    my $fy = -15;
    my $fx = 0;
    $gfx -> strokecolor("black");
    $gfx -> fillcolor("black");
    my $txt = $page->text();
    $gfx->move($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line from start to x - 11 inches.
    $fx -= 11;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to y + 24 inches
    $fy += 24;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x + 6 inches, y + 12 inches
    $fx += 6;
    $fy += 6;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x + 10 inches
    $fx += 10;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x + 6, y - 12 inches
    $fx += 6;
    $fy -= 6;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to y - 24 inches
    $fy -= 24;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x - 11 inches
    $fx -= 11;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  lint to x + 6 inches, y - 6 inches
    $gfx->stroke();
    # splat in the txt
    $txt -> strokecolor("black");
    $txt -> fillcolor("black");
    $txt->font($pdf->corefont('Helvetica Bold'), round(48 * $image_scale, 0));
    $txt->position($zx - 20 * $image_scale, $zy + i2ps(13, $image_scale));
    $txt->text ("3");
    $txt->crlf();
    $txt -> strokecolor("white");
    $txt -> fillcolor("white");
    $txt->crlf();
    $txt->crlf();
    $txt->crlf();
    $txt->crlf();
    $txt->text ("4");
    $txt->crlf();
    $txt->crlf();
    $txt->crlf();
    $txt->crlf();
    $txt->crlf();
    $txt->text ("5");
    $txt->crlf();
    $txt->crlf();
    $txt->crlf();
    $txt->crlf();
    $txt->crlf();
    $txt->crlf();
    $txt->text ("V");
    # move up 3 inches
    $fy += 4;
    $gfx->move($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $fx -= 8;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $fy += 18;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $fx += 4;
    $fy += 4;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $fx += 8;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $fx += 4;
    $fy -= 4;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to y - 24 inches
    $fy -= 18;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x - 11 inches
    $fx -= 8;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  lint to x + 6 inches, y - 6 inches
    $gfx->paint();
    # splat in the txt
    $txt -> strokecolor("white");
    $txt -> fillcolor("white");
    $txt->font($pdf->corefont('Helvetica Bold'), round(32 * $image_scale, 0));
    $txt->position($zx + i2ps(0, $image_scale), $zy + i2ps(0, $image_scale));
    $txt->text ("4");
    $txt->crlf();
    # move up 3 inches
    $gfx -> strokecolor("white");
    $fy += 3;
    $gfx->move($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $fx -= 5;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $fy += 12;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $fx += 3;
    $fy += 3;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $fx += 4;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    $fx += 3;
    $fy -= 3;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to y - 24 inches
    $fy -= 12;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  line to x - 11 inches
    $fx -= 5;
    $gfx->line($zx + i2ps($fx, $image_scale), $zy + i2ps($fy, $image_scale));
    #  lint to x + 6 inches, y - 6 inches
    $gfx->stroke();
}

sub makeCHASTarget($$$$) {
    my($paper, $distance, $equiv, $descr) = @_;

    my $pdf  = PDF::API2->new;
    my $trim = 0;
    my $orientation = "Portrait";

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
    my $real_height = 36 * 72;

    my ($scale_width, $scale_height) =
	scaled_dimensions($x2 - $x1, $y2 - $y1, $real_width, $real_height);

    my $image_scale = $scale_height / $real_height;

    if ($distance > 0) {
	$image_scale = $distance / $equiv;
    }
    my $width_inches = round($scale_width / 72, 1);
    my $height_inches = round($scale_height / 72, 1);

    my $delta_h = ($y2 - $y1 - $scale_height) / 2;
    my $delta_w = ($x2 - $x1 - $scale_width) / 2;

    # Find the centre of the page.
    my $midx = ($x2 - $x1) / 2 + $x1;
    my $midy = ($y2 - $y1) / 2 + $y1;

    # Draw our figures on the target in the correct locations. 
    $gfx -> strokecolor("black");
    figure_chas($gfx, $page, $pdf, $midx, $midy, $image_scale);

    # Put text on target, we use grey to be visible in both the black and
    # white portions of the target.
    $txt -> fillcolor("black");
    $txt -> strokecolor("black");
    $txt->font($pdf->corefont('Helvetica Bold'), 10);
    $txt->position($trim ?  $x1 + 10 : $x1 + 30, $trim ? $y2 - 10 : $y2 - 30);

    my $print_scale = round($image_scale, 3);
    my $real_bull_radius = 3 * 72;
    my $vmm = round((($real_bull_radius * 2) * ($image_scale * scale_base)) * mm, 0);
    my $tmm = round(((22 * 72) * ($image_scale * scale_base)) * mm, 0);
    my $hmm = round(((30 * 72) * ($image_scale * scale_base)) * mm, 0);
    $txt->text ("CHAS service rifle $descr. ");
    if ($image_scale != 1) {
	$txt->text ("Scale $distance / $equiv " );
    }
    $txt->font($pdf->corefont('Helvetica'), 8);
    $txt->crlf();
    $txt->text ("Must be printed on $paper paper with no scaling.");
    $txt->crlf();
    $txt->text ("V ring should be $vmm mm wide, Target should be $tmm mm wide and $hmm mm tall");
    $txt->crlf();
    if ($image_scale != 1) {
	shootat($txt, 200, $image_scale);
	shootat($txt, 300, $image_scale);
	shootat($txt, 500, $image_scale);
    }

    # Draw bull and magpie we use a grey ring to be
    # visible on both the black and white portions
    # of the target
    $gfx -> strokecolor("white");

    # 2/3 becausw we decided the 2/3 target is the real one.
    my $bull_radius = $real_bull_radius * ($image_scale * scale_base);
    $gfx -> circle( $midx, $midy, $bull_radius);
    $gfx -> stroke();

    $gfx -> strokecolor("white");
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
my $Paper = $cgi->param('Paper') || "Letter";
my $Orientation = $cgi->param('Orientation') || "Portrait";
my $Metres = $cgi->param('Metres');
my $Equiv = $cgi->param('Equiv');

my $CHAS = $cgi->param('CHAS');

my $Descr = "";

if ($CHAS eq "Centrefire") {
    $Metres = "300";
    $Equiv = "300";
    $Paper = "18x24";
    $Descr = "centrefire target"
} elsif ($CHAS eq "Rimfire-100") {
    $Metres = "100";
    $Equiv = "300";
    $Paper = "Letter";
    $Descr = "rimfire 100M equiv to 300M";
} elsif ($CHAS eq "Rimfire-50") {
    $Metres = "50";
    $Equiv = "200";
    $Paper = "Letter";
    $Descr = "rimfire 50M equiv to 200M";
} elsif ($CHAS eq "Norway") {
    $Metres = "200";
    $Equiv = "300";
    $Paper = "11x17";
    $Descr = "centrefire Norway match target";
} elsif ($CHAS eq "Norway-Rimfire-100") {
    $Metres = "66.7";
    $Equiv = "300";
    $Paper = "Letter";
    $Descr = "rimfire Norway match 100M equiv to 300M";
} elsif ($CHAS eq "Norway-Rimfire-50") {
    $Metres = "33.3";
    $Equiv = "200";
    $Paper = "Letter";
    $Descr = "rimfire Norway match 50M equiv to 200M";
} elsif ($CHAS eq "100M-200") {
    $Metres = "100";
    $Equiv = "200";
    $Paper = "Legal";
    $Descr = "PRACTICE at 100 M, equiv to 200M";
} elsif ($CHAS eq "100M-500") {
    $Metres = "100";
    $Equiv = "500";
    $Paper = "Letter";
    $Descr = "PRACTICE at 100 M, equiv to 500M";
} elsif ($CHAS eq "50M-300") {
    $Metres = "50";
    $Equiv = "300";
    $Paper = "Letter";
    $Descr = "PRACTICE at 50 M, equiv to 200M";
} elsif ($CHAS eq "40Y-300") {
    $Metres = "36.6";
    $Equiv = "300";
    $Paper = "Letter";
    $Descr = "PRACTICE at 40 Yards, equiv to 300M";
} elsif ($CHAS eq "40Y-300") {
    $Metres = "36.6";
    $Equiv = "300";
    $Paper = "Letter";
    $Descr = "PRACTICE at 40 Yards, equiv to 300M";
} elsif ($CHAS eq "40Y-200") {
    $Metres = "36.6";
    $Equiv = "200";
    $Paper = "Letter";
    $Descr = "PRACTICE at 40 Yards, equiv to 200M";
} elsif ($CHAS eq "25Y-300") {
    $Metres = "22.9";
    $Equiv = "300";
    $Paper = "Letter";
    $Descr = "PRACTICE at 25 Yards, equiv to 300M";
} elsif ($CHAS eq "25Y-200") {
    $Metres = "22.9";
    $Equiv = "300";
    $Paper = "Letter";
    $Descr = "PRACTICE at 25 Yards, equiv to 200M";
}

my @papers= ("A0", "A1", "A2", "A3", "A4", "Letter", "Legal", "11x17", "12x18", "18x24", "24x36", "36x36", "36x48", "48x36", "72x36", "48x48", "64x48", "96x48", "24x72", "48x72", "72x72", "96x72", "144x72");

die "Paper $Paper is not valid"
    unless (grep(/^$Paper$/, @papers));

my $pdfstring;
$pdfstring = makeCHASTarget($Paper, $Metres, $Equiv, $Descr);

print $cgi->header('application/pdf');
print $pdfstring;
