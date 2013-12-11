module counter ( clk, value, reset, carry_out );
  output [1:0] value;
  input clk, reset;
  output carry_out;
  wire N5,N6,N7,n4,n5,n6;
  wire [1:0] n7;

  DFF_X1 \value_reg[0]  ( .D(N5), .CK(clk), .Q(value[0]), .QN(n5) );
  DFF_X1 \value_reg[1]  ( .D(N6), .CK(clk), .Q(value[1]), .QN(n4) );
  DFF_X1 carry_out_reg ( .D(N7), .CK(clk), .Q(carry_out) );
  NOR3_X1 U9 ( .A1(n4), .A2(reset), .A3(n5), .ZN(N7) );
  MUX2_X1 U10 ( .A(N5), .B(n6), .S(n4), .Z(N6) );
  NOR2_X1 U11 ( .A1(reset), .A2(n5), .ZN(n6) );
  NOR2_X1 U12 ( .A1(reset), .A2(value[0]), .ZN(N5) );
endmodule
