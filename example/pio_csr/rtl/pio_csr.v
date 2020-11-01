///////////////////////////////////////////////////////////////
//
// Generated by Simple CSR Generator
//
// Name: pio_csr.v
// Date Created: 11/1/2020 - 14:29
//
// Description:
//  CSR module for pio
//
///////////////////////////////////////////////////////////////


module pio_csr
(
  input            clk,
  input            reset,
  input  [3:0]     i_sw_address,
  input            i_sw_read,
  input            i_sw_write,
  input            i_sw_select,
  input  [31:0]    i_sw_wrdata,
  output [31:0]    o_sw_rddata,
  input  [31:0]    i_hw_pio_read_data,
  output [31:0]    o_hw_pio_write_data,
  output           o_hw_pio_ctrl_status_level_capture_en,
  input            i_hw_pio_ctrl_status_level_captured,
  input  [13:0]    i_hw_pio_ctrl_status_sample
);


  // register definition
  reg    [31:0]    o_sw_rddata_q;
  reg    [31:0]    i_hw_pio_read_data_q;
  reg    [31:0]    o_hw_pio_write_data_q;
  reg              o_hw_pio_ctrl_status_level_capture_en_q;
  reg              i_hw_pio_ctrl_status_level_captured_q;
  reg    [13:0]    i_hw_pio_ctrl_status_sample_q;

  // reg type variable definition
  reg    [31:0]    o_sw_rddata_next;
  reg              o_hw_pio_write_data_q_wen;
  reg              o_hw_pio_ctrl_status_level_capture_en_q_wen;
  reg              i_hw_pio_ctrl_status_sample_q_wen;


  //==============================
  // HW Read output
  //==============================

  assign o_sw_rddata = o_sw_rddata_q;
  assign o_hw_pio_write_data = o_hw_pio_write_data_q;
  assign o_hw_pio_ctrl_status_level_capture_en = o_hw_pio_ctrl_status_level_capture_en_q;


  //==============================
  // Software Read Logic
  //==============================

  always @(posedge clk) begin
    if (i_sw_read) o_sw_rddata_q <= o_sw_rddata_next;
  end

  // read decode logic
  always @(*) begin
    o_sw_rddata_next = o_sw_rddata;
    case(i_sw_address)
      4'h0:  o_sw_rddata_next = {i_hw_pio_read_data_q};
      4'h4:  o_sw_rddata_next = {o_hw_pio_write_data_q};
      4'h8:  o_sw_rddata_next = {1'b0, i_hw_pio_ctrl_status_sample_q, 
                                 i_hw_pio_ctrl_status_level_captured_q, 
                                 15'b0, 
                                 o_hw_pio_ctrl_status_level_capture_en_q};
      default:  o_sw_rddata_next = o_sw_rddata;
    endcase
  end



  //==============================
  // Software/Hardware Write Logic
  //==============================

  // software write decode Logic
  always @(*) begin
        o_hw_pio_write_data_q_wen = 1'b0;
        o_hw_pio_ctrl_status_level_capture_en_q_wen = 1'b0;
        i_hw_pio_ctrl_status_sample_q_wen = 1'b0;
    case(i_sw_address)
      4'h4: begin
        o_hw_pio_write_data_q_wen = i_sw_write & i_sw_select;
      end
      4'h8: begin
        o_hw_pio_ctrl_status_level_capture_en_q_wen = i_sw_write & i_sw_select;
        i_hw_pio_ctrl_status_sample_q_wen = i_sw_write & i_sw_select;
      end
      default: begin
        o_hw_pio_write_data_q_wen = 1'b0;
        o_hw_pio_ctrl_status_level_capture_en_q_wen = 1'b0;
        i_hw_pio_ctrl_status_sample_q_wen = 1'b0;
      end
    endcase
  end


  // write sequential Logic
  // Software/Hardware Write Logic
  always @(posedge clk) begin
    if (reset) begin
      i_hw_pio_read_data_q <= 32'h0;
      o_hw_pio_write_data_q <= 32'hdeadbeef;
      o_hw_pio_ctrl_status_level_capture_en_q <= 1'h1;
      i_hw_pio_ctrl_status_level_captured_q <= 1'h0;
      i_hw_pio_ctrl_status_sample_q <= 14'hab;
    end
    else begin
      // Register: pio_read | Field: i_hw_pio_read_data
      i_hw_pio_read_data_q <= i_hw_pio_read_data;

      // Register: pio_write | Field: o_hw_pio_write_data
      if (o_hw_pio_write_data_q_wen) o_hw_pio_write_data_q <= i_sw_wrdata[31:0];

      // Register: pio_ctrl_status | Field: o_hw_pio_ctrl_status_level_capture_en
      if (o_hw_pio_ctrl_status_level_capture_en_q_wen) o_hw_pio_ctrl_status_level_capture_en_q <= i_sw_wrdata[0:0];

      // Register: pio_ctrl_status | Field: i_hw_pio_ctrl_status_level_captured
      i_hw_pio_ctrl_status_level_captured_q <= i_hw_pio_ctrl_status_level_captured;

      // Register: pio_ctrl_status | Field: i_hw_pio_ctrl_status_sample
      if (i_hw_pio_ctrl_status_sample_q_wen) i_hw_pio_ctrl_status_sample_q <= i_sw_wrdata[30:17];
      else i_hw_pio_ctrl_status_sample_q <= i_hw_pio_ctrl_status_sample;

    end
  end

  //==============================
  // FIFO control
  //==============================

  // FIFO Read logic

  // FIFO Write logic


endmodule
