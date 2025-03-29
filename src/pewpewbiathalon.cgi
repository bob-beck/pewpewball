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
# Print equivalent shooting distance to original in yards.
sub shootat($$$) {
    my ($txt, $distance, $scale) = @_;
    my $metres = round(50 * $scale, 0);
    my $yards = round($metres / YardsPerMetre, 0);
    $txt->text("Shooting at $metres M ($yards Yds) is equivalent to the official target at 50 M");
    $txt->crlf();
}

sub makeBiathalonTarget($$$$) {
    my($paper, $distance, $equiv, $type) = @_;

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

    my $real_diameter = 45 / mm;
    if ($type eq "standing") {
	$real_diameter = 115 / mm;
    }

    my $image_scale = $distance / $equiv;

    # Find the centre of the page.
    my $midx = ($x2 - $x1) / 2 + $x1;
    my $midy = ($y2 - $y1) / 2 + $y1;

    # Draw our figures on the target in the correct locations. 
    $gfx -> strokecolor("black");

    # Put text on target, we use grey to be visible in both the black and
    # white portions of the target.
    $txt -> fillcolor("black");
    $txt -> strokecolor("black");
    $txt->font($pdf->corefont('Helvetica Bold'), 10);
    $txt->position($trim ?  $x1 + 10 : $x1 + 30, $trim ? $y2 - 10 : $y2 - 30);

    my $print_scale = round($image_scale, 3);
    my $real_bull_radius = $real_diameter / 2;
    my $vmm = round($real_diameter * $image_scale * mm, 0);

    my $descr = "Biathalon Prone Centre Only Target";
    if ($real_diameter == 115 / mm) {
	$descr = "Biathalon Target";
    }
    $txt->text ("$descr");
    if ($image_scale != 1) {
	$txt->text (" (Scale $distance / $equiv) " );
    } else {
	$txt->text (" (Official Size) " );
    }
    
    $txt->font($pdf->corefont('Helvetica'), 8);
    $txt->crlf();
    $txt->text ("Must be printed on $paper paper with no scaling.");
    $txt->crlf();
    $txt->text ("Target should be $vmm mm wide");
    $txt->crlf();
    if ($image_scale != 1) {
	shootat($txt, $distance, $image_scale);
    }

    $gfx -> strokecolor("black");
    my $bull_radius = $real_bull_radius * $image_scale;
    $gfx -> circle( $midx, $midy, $bull_radius);
    $gfx -> paint();

    if ($real_diameter == 115 / mm) {
	# Make the 45mm scoring ring.
	$gfx -> strokecolor("grey");
	my $centre_diameter = 45 / mm * $image_scale;
	$gfx -> circle($midx, $midy, $centre_diameter / 2);
	$gfx -> stroke();
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
my $Equiv = "50";
my $Type = $cgi->param('Type');

my @papers= ("A0", "A1", "A2", "A3", "A4", "Letter", "Legal", "11x17", "12x18", "18x24", "24x36", "36x36", "36x48", "48x36", "72x36", "48x48", "64x48", "96x48", "24x72", "48x72", "72x72", "96x72", "144x72");

die "Paper $Paper is not valid"
    unless (grep(/^$Paper$/, @papers));

my $pdfstring;
$pdfstring = makeBiathalonTarget($Paper, $Metres, $Equiv, $Type);

print $cgi->header('application/pdf');
print $pdfstring;
